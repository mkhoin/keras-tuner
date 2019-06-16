# Copyright 2019 The Keras Tuner Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"Trial base class."

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy

from . import execution as execution_module
from . import metrics_tracking


class Trial(object):
    """Trial base class.

    Not to be subclassed.
    """

    def __init__(self, trial_id, model, hyperparameters, objective,
                 tuner=None, cloudservice=None):
        self.trial_id = trial_id
        self.model = model
        self.executions = []
        self.hyperparameters = hyperparameters.copy()
        self.objective = objective

        self.tuner = tuner
        self.cloudservice = cloudservice

        # Per-epoch metrics averages across all executions
        self.averaged_metrics = metrics_tracking.MetricsTracker(model.metrics)
        self.score = None  # Score of the trial: best objective value achieved.

    def run_execution(self, *fit_args, **fit_kwargs):
        execution_id = str(len(self.executions))
        execution = execution_module.Execution(
            execution_id,
            self.model,
            trial=self, tuner=self.tuner, cloudservice=self.cloudservice)
        self.executions.append(execution)
        execution.run(*fit_args, **fit_kwargs)

        # Note that self.averaged_metrics is updated in a callback.

        self.score = self.averaged_metrics.get_best_value(self.objective)
        return execution

    def summary(self):
        # TODO
        pass

    def get_status(self):
        return {
            'trial_id': self.trial_id,
            'model': self.model.get_config(),
            'hyperparameters': self.hyperparameters.get_config(),
            'objective': self.objective,
            'averaged_metrics': self.averaged_metrics.get_config(),
            'score': self.score
        }