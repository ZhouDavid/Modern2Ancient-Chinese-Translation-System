from __future__ import print_function
import numpy as np
import os
from cntk import Trainer, Axis
from cntk.io import MinibatchSource, CTFDeserializer, StreamDef, StreamDefs, INFINITELY_REPEAT
from cntk.learner import momentum_sgd, momentum_as_time_constant_schedule, learning_rate_schedule, UnitType
from cntk.ops import input_variable, cross_entropy_with_softmax, classification_error, sequence, past_value, future_value, element_select, \
                     alias, hardmax, placeholder_variable, combine, parameter, plus, times
from cntk.ops.functions import CloneMethod
from cntk.blocks import LSTM, Stabilizer
from cntk.initializer import glorot_uniform
from cntk.utils import get_train_eval_criterion, get_train_loss
# Select the right target device when this notebook is being tested:
if 'TEST_DEVICE' in os.environ:
    import cntk
    if os.environ['TEST_DEVICE'] == 'cpu':
        cntk.device.set_default_device(cntk.device.cpu())
    else:
        cntk.device.set_default_device(cntk.device.gpu(0))
import requests

def download(url, filename):
    """ utility function to download a file """
    response = requests.get(url, stream=True)
    with open(filename, "wb") as handle:
        for data in response.iter_content():
            handle.write(data)

data_dir = os.path.join('..', 'Examples', 'SequenceToSequence', 'CMUDict', 'Data')
# If above directory does not exist, just use current.
if not os.path.exists(data_dir):
    data_dir = '.'

valid_file = os.path.join(data_dir, 'tiny.ctf')
train_file = os.path.join(data_dir, 'cmudict-0.7b.train-dev-20-21.ctf')
vocab_file = os.path.join(data_dir, 'cmudict-0.7b.mapping')

files = [valid_file, train_file, vocab_file]

for file in files:
    if os.path.exists(file):
        print("Reusing locally cached: ", file)
    else:
        url = "https://github.com/Microsoft/CNTK/blob/v2.0.beta10.0/Examples/SequenceToSequence/CMUDict/Data/%s?raw=true"%file
        print("Starting download:", file)
        download(url, file)
        print("Download completed")

isFast = True
# Helper function to load the model vocabulary file
def get_vocab(path):
    # get the vocab for printing output sequences in plaintext
    vocab = [w.strip() for w in open(path).readlines()]
    i2w = { i:ch for i,ch in enumerate(vocab) }

    return (vocab, i2w)

# Read vocabulary data and generate their corresponding indices
vocab, i2w = get_vocab(vocab_file)

input_vocab_size = len(vocab)
label_vocab_size = len(vocab)
# Print vocab and the correspoding mapping to the phonemes
print("Vocabulary size is", len(vocab))
print("First 15 letters are:")
print(vocab[:15])
print()
print("Print dictionary with the vocabulary mapping:")
print(i2w)
def create_reader(path, randomize, size=INFINITELY_REPEAT):
    return MinibatchSource(CTFDeserializer(path, StreamDefs(
        features  = StreamDef(field='S0', shape=input_vocab_size, is_sparse=True),
        labels    = StreamDef(field='S1', shape=label_vocab_size, is_sparse=True)
    )), randomize=randomize, epoch_size = size)

# Train data reader
train_reader = create_reader(train_file, True)

# Validation/Test data reader
valid_reader = create_reader(valid_file, False)
model_dir = "." # we downloaded our data to the local directory above # TODO check me

# model dimensions
input_vocab_dim  = input_vocab_size
label_vocab_dim  = label_vocab_size
hidden_dim = 128
num_layers = 1
# Source and target inputs to the model
batch_axis = Axis.default_batch_axis()
input_seq_axis = Axis('inputAxis')
label_seq_axis = Axis('labelAxis')

input_dynamic_axes = [batch_axis, input_seq_axis]
raw_input = input_variable(shape=(input_vocab_dim), dynamic_axes=input_dynamic_axes, name='raw_input')

label_dynamic_axes = [batch_axis, label_seq_axis]
raw_labels = input_variable(shape=(label_vocab_dim), dynamic_axes=label_dynamic_axes, name='raw_labels')
# Instantiate the sequence to sequence translation model
input_sequence = raw_input

# Drop the sentence start token from the label, for decoder training
label_sequence = sequence.slice(raw_labels,
                       1, 0, name='label_sequence') # <s> A B C </s> --> A B C </s>
label_sentence_start = sequence.first(raw_labels)   # <s>

is_first_label = sequence.is_first(label_sequence)  # 1 0 0 0 ...
label_sentence_start_scattered = sequence.scatter(  # <s> 0 0 0 ... (up to the length of label_sequence)
    label_sentence_start, is_first_label)
def LSTM_layer(input, output_dim, recurrence_hook_h=past_value, recurrence_hook_c=past_value):
    # we first create placeholders for the hidden state and cell state which we don't have yet
    dh = placeholder_variable(shape=(output_dim), dynamic_axes=input.dynamic_axes)
    dc = placeholder_variable(shape=(output_dim), dynamic_axes=input.dynamic_axes)

    # we now create an LSTM_cell function and call it with the input and placeholders
    LSTM_cell = LSTM(output_dim)
    f_x_h_c = LSTM_cell(input, (dh, dc))
    h_c = f_x_h_c.outputs

    # we setup the recurrence by specifying the type of recurrence (by default it's `past_value` -- the previous value)
    h = recurrence_hook_h(h_c[0])
    c = recurrence_hook_c(h_c[1])

    replacements = { dh: h.output, dc: c.output }
    f_x_h_c.replace_placeholders(replacements)

    h = f_x_h_c.outputs[0]
    c = f_x_h_c.outputs[1]

    # and finally we return the hidden state and cell state as functions (by using `combine`)
    return combine([h]), combine([c])
    # 1.
# Create the encoder (set the output_dim to hidden_dim which we defined earlier).

(encoder_output_h, encoder_output_c) = LSTM_layer(input_sequence, hidden_dim)

# 2.
# Set num_layers to something higher than 1 and create a stack of LSTMs to represent the encoder.
num_layers = 2
output_h = alias(input_sequence) # get a copy of the input_sequence
for i in range(0, num_layers):
    (output_h, output_c) = LSTM_layer(output_h.output, hidden_dim)

# 3.
# Get the output of the encoder and put it into the right form to be passed into the decoder [hard]
thought_vector_h = sequence.first(output_h)
thought_vector_c = sequence.first(output_c)

thought_vector_broadcast_h = sequence.broadcast_as(thought_vector_h, label_sequence)
thought_vector_broadcast_c = sequence.broadcast_as(thought_vector_c, label_sequence)

# 4.
# Reverse the order of the input_sequence (this has been shown to help especially in machine translation)
(encoder_output_h, encoder_output_c) = LSTM_layer(input_sequence, hidden_dim, future_value, future_value)
decoder_input = element_select(is_first_label, label_sentence_start_scattered, past_value(label_sequence))
(output_h, output_c) = LSTM_layer(input_sequence, hidden_dim,
                                  recurrence_hook_h=past_value, recurrence_hook_c=past_value)
# 1.
# Create the recurrence hooks for the decoder LSTM.

recurrence_hook_h = lambda operand: element_select(is_first_label, thought_vector_broadcast_h, past_value(operand))
recurrence_hook_c = lambda operand: element_select(is_first_label, thought_vector_broadcast_c, past_value(operand))

# 2.
# With your recurrence hooks, create the decoder.

(decoder_output_h, decoder_output_c) = LSTM_layer(decoder_input, hidden_dim, recurrence_hook_h, recurrence_hook_c)

# 3.
# Create a decoder with multiple layers.
# Note that you will have to use different recurrence hooks for the lower layers

num_layers = 3
decoder_output_h = alias(decoder_input)
for i in range(0, num_layers):
    if (i > 0):
        recurrence_hook_h = past_value
        recurrence_hook_c = past_value
    else:
        recurrence_hook_h = lambda operand: element_select(
            is_first_label, thought_vector_broadcast_h, past_value(operand))
        recurrence_hook_c = lambda operand: element_select(
            is_first_label, thought_vector_broadcast_c, past_value(operand))

    (decoder_output_h, decoder_output_c) = LSTM_layer(decoder_output_h.output, hidden_dim,
                                                      recurrence_hook_h, recurrence_hook_c)
    # 1.
# Add the linear layer

W = parameter(shape=(decoder_output_h.shape[0], label_vocab_dim), init=glorot_uniform())
B = parameter(shape=(label_vocab_dim), init=0)
z = plus(B, times(decoder_output_h, W))
def create_model():

    # Source and target inputs to the model
    batch_axis = Axis.default_batch_axis()
    input_seq_axis = Axis('inputAxis')
    label_seq_axis = Axis('labelAxis')

    input_dynamic_axes = [batch_axis, input_seq_axis]
    raw_input = input_variable(
        shape=(input_vocab_dim), dynamic_axes=input_dynamic_axes, name='raw_input')

    label_dynamic_axes = [batch_axis, label_seq_axis]
    raw_labels = input_variable(
        shape=(label_vocab_dim), dynamic_axes=label_dynamic_axes, name='raw_labels')

    # Instantiate the sequence to sequence translation model
    input_sequence = raw_input

    # Drop the sentence start token from the label, for decoder training
    label_sequence = sequence.slice(raw_labels, 1, 0,
                                    name='label_sequence') # <s> A B C </s> --> A B C </s>
    label_sentence_start = sequence.first(raw_labels)      # <s>

    # Setup primer for decoder
    is_first_label = sequence.is_first(label_sequence)  # 1 0 0 0 ...
    label_sentence_start_scattered = sequence.scatter(
        label_sentence_start, is_first_label)

    # Encoder
    stabilize = Stabilizer()
    encoder_output_h = stabilize(input_sequence)
    for i in range(0, num_layers):
        (encoder_output_h, encoder_output_c) = LSTM_layer(
            encoder_output_h.output, hidden_dim, future_value, future_value)

    # Prepare encoder output to be used in decoder
    thought_vector_h = sequence.first(encoder_output_h)
    thought_vector_c = sequence.first(encoder_output_c)

    thought_vector_broadcast_h = sequence.broadcast_as(
        thought_vector_h, label_sequence)
    thought_vector_broadcast_c = sequence.broadcast_as(
        thought_vector_c, label_sequence)

    # Decoder
    decoder_history_hook = alias(label_sequence, name='decoder_history_hook') # copy label_sequence

    decoder_input = element_select(is_first_label, label_sentence_start_scattered, past_value(
        decoder_history_hook))

    decoder_output_h = stabilize(decoder_input)
    for i in range(0, num_layers):
        if (i > 0):
            recurrence_hook_h = past_value
            recurrence_hook_c = past_value
        else:
            recurrence_hook_h = lambda operand: element_select(
                is_first_label, thought_vector_broadcast_h, past_value(operand))
            recurrence_hook_c = lambda operand: element_select(
                is_first_label, thought_vector_broadcast_c, past_value(operand))

        (decoder_output_h, decoder_output_c) = LSTM_layer(
            decoder_output_h.output, hidden_dim, recurrence_hook_h, recurrence_hook_c)

    # Linear output layer
    W = parameter(shape=(decoder_output_h.shape[0], label_vocab_dim), init=glorot_uniform())
    B = parameter(shape=(label_vocab_dim), init=0)
    z = plus(B, times(stabilize(decoder_output_h), W))

    return z
model = create_model()
label_sequence = model.find_by_name('label_sequence')

# Criterion nodes
ce = cross_entropy_with_softmax(model, label_sequence)
errs = classification_error(model, label_sequence)

# let's show the required arguments for this model
print([x.name for x in model.arguments])
lr_per_sample = learning_rate_schedule(0.007, UnitType.sample)
minibatch_size = 72
momentum_time_constant = momentum_as_time_constant_schedule(1100)
clipping_threshold_per_sample = 2.3
gradient_clipping_with_truncation = True
learner = momentum_sgd(model.parameters,
                        lr_per_sample, momentum_time_constant,
                        gradient_clipping_threshold_per_sample=clipping_threshold_per_sample,
                        gradient_clipping_with_truncation=gradient_clipping_with_truncation)
trainer = Trainer(model, ce, errs, learner)
# helper function to find variables by name
def find_arg_by_name(name, expression):
    vars = [i for i in expression.arguments if i.name == name]
    assert len(vars) == 1
    return vars[0]

train_bind = {
        find_arg_by_name('raw_input' , model) : train_reader.streams.features,
        find_arg_by_name('raw_labels', model) : train_reader.streams.labels
    }
training_progress_output_freq = 100
max_num_minibatch = 100 if isFast else 1000

for i in range(max_num_minibatch):
    # get next minibatch of training data
    mb_train = train_reader.next_minibatch(minibatch_size, input_map=train_bind)
    trainer.train_minibatch(mb_train)

    # collect epoch-wide stats
    if i % training_progress_output_freq == 0:
        print("Minibatch: {0}, Train Loss: {1:.3f}, Train Evaluation Criterion: {2:2.3f}".format(i,
                        get_train_loss(trainer), get_train_eval_criterion(trainer)))
decoder_history_hook = alias(label_sequence, name='decoder_history_hook') # copy label_sequence
decoder_input = element_select(is_first_label, label_sentence_start_scattered, past_value(decoder_history_hook))
model = create_model()

# get some references to the new model
label_sequence = model.find_by_name('label_sequence')
decoder_history_hook = model.find_by_name('decoder_history_hook')

# and now replace the output of decoder_history_hook with the hardmax output of the network
def clone_and_hook():
    # network output for decoder history
    net_output = hardmax(model)

    # make a clone of the graph where the ground truth is replaced by the network output
    return model.clone(CloneMethod.share, {decoder_history_hook.output : net_output.output})

# get a new model that uses the past network output as input to the decoder
new_model = clone_and_hook()
########################
# train action         #
########################

def train(train_reader, valid_reader, vocab, i2w, model, max_epochs):

    # do some hooks that we won't need in the future
    label_sequence = model.find_by_name('label_sequence')
    decoder_history_hook = model.find_by_name('decoder_history_hook')

    # Criterion nodes
    ce = cross_entropy_with_softmax(model, label_sequence)
    errs = classification_error(model, label_sequence)

    def clone_and_hook():
        # network output for decoder history
        net_output = hardmax(model)

        # make a clone of the graph where the ground truth is replaced by the network output
        return model.clone(CloneMethod.share, {decoder_history_hook.output : net_output.output})

    # get a new model that uses the past network output as input to the decoder
    new_model = clone_and_hook()

    # Instantiate the trainer object to drive the model training
    lr_per_sample = learning_rate_schedule(0.007, UnitType.sample)
    minibatch_size = 72
    momentum_time_constant = momentum_as_time_constant_schedule(1100)
    clipping_threshold_per_sample = 2.3
    gradient_clipping_with_truncation = True
    learner = momentum_sgd(model.parameters,
                           lr_per_sample, momentum_time_constant,
                           gradient_clipping_threshold_per_sample=clipping_threshold_per_sample,
                           gradient_clipping_with_truncation=gradient_clipping_with_truncation)
    trainer = Trainer(model, ce, errs, learner)

    # Get minibatches of sequences to train with and perform model training
    i = 0
    mbs = 0

    # Set epoch size to a larger number of lower training error
    epoch_size = 5000 if isFast else 908241

    training_progress_output_freq = 100

    # bind inputs to data from readers
    train_bind = {
        find_arg_by_name('raw_input' , model) : train_reader.streams.features,
        find_arg_by_name('raw_labels', model) : train_reader.streams.labels
    }
    valid_bind = {
        find_arg_by_name('raw_input' , new_model) : valid_reader.streams.features,
        find_arg_by_name('raw_labels', new_model) : valid_reader.streams.labels
    }

    for epoch in range(max_epochs):
        loss_numer = 0
        metric_numer = 0
        denom = 0

        while i < (epoch+1) * epoch_size:
            # get next minibatch of training data
            mb_train = train_reader.next_minibatch(minibatch_size, input_map=train_bind)
            trainer.train_minibatch(mb_train)

            # collect epoch-wide stats
            samples = trainer.previous_minibatch_sample_count
            loss_numer += trainer.previous_minibatch_loss_average * samples
            metric_numer += trainer.previous_minibatch_evaluation_average * samples
            denom += samples

            # every N MBs evaluate on a test sequence to visually show how we're doing; also print training stats
            if mbs % training_progress_output_freq == 0:

                print("Minibatch: {0}, Train Loss: {1:2.3f}, Train Evaluation Criterion: {2:2.3f}".format(mbs,
                      get_train_loss(trainer), get_train_eval_criterion(trainer)))

                mb_valid = valid_reader.next_minibatch(minibatch_size, input_map=valid_bind)
                e = new_model.eval(mb_valid)
                print_sequences(e, i2w)

            i += mb_train[find_arg_by_name('raw_labels', model)].num_samples
            mbs += 1

        print("--- EPOCH %d DONE: loss = %f, errs = %f ---" % (epoch, loss_numer/denom, 100.0*(metric_numer/denom)))
        return 100.0*(metric_numer/denom)
# Given a vocab and tensor, print the output
def print_sequences(sequences, i2w):
    for s in sequences:
        print([i2w[np.argmax(w)] for w in s], sep=" ")

# hook up data
train_reader = create_reader(train_file, True)
valid_reader = create_reader(valid_file, False)
vocab, i2w = get_vocab(vocab_file)

# create model
model = create_model()

# train
error = train(train_reader, valid_reader, vocab, i2w, model, max_epochs=1)
print(error)