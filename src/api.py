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

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from eat.core.components import Groupoid, TermOperation
from eat.beam_algorithm.beam import BeamEnumerationAlgorithm
app = Flask(__name__)
cors = CORS(app)


def run_beam_algorithm(groupoid, target):
    algorithm = "MFBA"
    mtgm = "random-term-generation"
    prob = 0.1
    beam_width = sub_beam_width = 2
    grp = Groupoid(groupoid)
    to = TermOperation(groupoid=grp, term_variables=["x", "y", "z"], target=target)
    beam = BeamEnumerationAlgorithm(
        grp,
        to,
        algorithm,
        male_term_generation_method=mtgm,
        term_expansion_probability=prob,
        beam_width=beam_width,
        sub_beam_width=sub_beam_width)
    node, search_time = beam.run(verbose=True)
    return node.term, search_time


@app.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def landing():
    return "Welcome to the Eat API"


@app.route('/runeat', methods=['POST'])
@cross_origin(supports_credentials=True)
def eat():
    data = request.get_json()  # Get the JSON data
    groupoid = [int(t) for t in data['groupoid']]
    target = [[t] for t in data['target']]
    term, search_time= run_beam_algorithm(groupoid, target)
    response = jsonify({'term': term, 'search_time': f"{search_time:.2f}"})
    return response


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
