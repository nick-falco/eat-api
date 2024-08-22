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

import logging
from multiprocessing import Process, Queue, Pipe
from flask import Flask, request
from flask import stream_with_context
from flask_cors import CORS, cross_origin
from eat.core.components import Groupoid, TermOperation
from eat.beam_algorithm.beam import BeamEnumerationAlgorithm
app = Flask(__name__)
cors = CORS(app)


class PipeHandler(logging.Handler):

    def __init__(self, conn):
        super().__init__()
        self.conn = conn

    def emit(self, record):
        log_entry = self.format(record)
        self.conn.send(log_entry)


def run_beam_algorithm_subprocess(groupoid, target, conn, queue):
    # capture the log output from the beam algorithm
    pipe_handler = PipeHandler(conn)

    algorithm = "MFBA"
    mtgm = "random-term-generation"
    prob = 0.1
    beam_width = sub_beam_width = 2
    grp = Groupoid(groupoid)
    to = TermOperation(groupoid=grp, term_variables=["x", "y", "z"],
                       target=target)
    beam = BeamEnumerationAlgorithm(
        grp,
        to,
        algorithm,
        male_term_generation_method=mtgm,
        term_expansion_probability=prob,
        beam_width=beam_width,
        sub_beam_width=sub_beam_width,
        logging_handler=pipe_handler)
    node, search_time = beam.run(verbose=True)
    queue.put((node.term, search_time))
    conn.close()


def run_beam_algorithm(groupoid, target):
    queue = Queue()
    parent_conn, child_conn = Pipe()
    p = Process(target=run_beam_algorithm_subprocess,
                args=(groupoid, target, child_conn, queue))
    p.start()

    while True:
        if parent_conn.poll():
            log_message = parent_conn.recv()
            print(log_message)
            yield log_message + '\n'
        if not p.is_alive():
            break
    p.join()
    term, search_time = queue.get()
    yield term + '\n'
    yield f"{search_time:.2f}" + '\n'


@app.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def landing():
    return "Welcome to the Eat API"


@app.route('/runeat', methods=['POST'])
@cross_origin(supports_credentials=True)
def eat():
    data = request.get_json()  # Get the JSON data
    groupoid = [int(t) for t in data['groupoid']]
    target = [[int(t)] for t in data['target']]

    # Use stream_with_context to stream the output
    response = app.response_class(
        stream_with_context(run_beam_algorithm(groupoid, target)),
        mimetype='text/plain'
    )
    return response


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
