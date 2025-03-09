from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'message': 'Root endpoint'})

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello from Flask!'})

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    return jsonify({'leaderboard': [ # TODO: get from database
        {
            'rank': 1,
            'name': 'AJS',
            'score': 100
        },
        {
            'rank': 2,
            'name': 'ABC',
            'score': 90
        },
        {
            'rank': 3,
            'name': 'WKE',
            'score': 80
        },
        {
            'rank': 4,
            'name': 'QWE',
            'score': 70
        }
    ]})

if __name__ == '__main__':
    # You can specify host='0.0.0.0' if you want it accessible externally
    app.run(debug=True, port=5000)