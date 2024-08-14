# Copyright 2019 Google LLC All Rights Reserved.
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

from flask import Flask
from eat.core.components import Groupoid, TermOperation
from eat.beam_algorithm.beam import BeamEnumerationAlgorithm
app = Flask(__name__)


def run_beam_algorithm():
    algorithm = "FBA"
    mtgm = "random-term-generation"
    prob = 0.1
    beam_width = sub_beam_width = 2
    grp = Groupoid([2, 1, 2, 1, 0, 0, 0, 0, 1])
    to = TermOperation(groupoid=grp, term_variables=["x", "y", "z"])
    beam = BeamEnumerationAlgorithm(
        grp,
        to,
        algorithm,
        male_term_generation_method=mtgm,
        term_expansion_probability=prob,
        beam_width=beam_width,
        sub_beam_width=sub_beam_width)
    node, _ = beam.run()
    return node

@app.route('/', methods=['GET'])
def landing():
    return "Welcome to the EAT API!"

@app.route('/runeat', methods=['GET'])
def eat():
    return run_beam_algorithm().term


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
