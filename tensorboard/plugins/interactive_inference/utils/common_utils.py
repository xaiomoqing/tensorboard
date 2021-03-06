# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Common utils for all inference plugin files."""

from tensorflow_serving.apis import classification_pb2
from tensorflow_serving.apis import regression_pb2


class InvalidUserInputError(Exception):
  """An exception to throw if user input is detected to be invalid.

  Attributes:
    original_exception: The triggering `Exception` object to be wrapped, or
      a string.
  """

  def __init__(self, original_exception):
    """Inits InvalidUserInputError."""
    self.original_exception = original_exception
    Exception.__init__(self)

  @property
  def message(self):
    return 'InvalidUserInputError: ' + str(self.original_exception)


def convert_predict_response(pred, serving_bundle):
  """Converts a PredictResponse to ClassificationResponse or RegressionResponse.

  Args:
    pred: PredictResponse to convert.
    serving_bundle: A `ServingBundle` object that contains the information about
      the serving request that the response was generated by.

  Returns:
    A ClassificationResponse or RegressionResponse.
  """
  output = pred.outputs[serving_bundle.predict_output_tensor]
  raw_output = output.float_val
  output_index = 0
  if serving_bundle.model_type == 'classification':
    response = classification_pb2.ClassificationResponse()
    response.model_spec.CopyFrom(pred.model_spec)
    for _ in range(output.tensor_shape.dim[0].size):
      classification = response.result.classifications.add()
      for class_index in range(output.tensor_shape.dim[1].size):
        class_score = classification.classes.add()
        class_score.score = raw_output[output_index]
        output_index += 1
        class_score.label = str(class_index)
  else:
    response = regression_pb2.RegressionResponse()
    response.model_spec.CopyFrom(pred.model_spec)
    for _ in range(output.tensor_shape.dim[0].size):
      regression = response.result.regressions.add()
      regression.value = raw_output[output_index]
      output_index += 1
  return response
