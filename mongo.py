from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from functools import wraps
import json

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'python_mongo_test'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/'

mongo = PyMongo(app)


def filter_query(omit):
  def endpoint_wrapper(func):
    @wraps(func)
    def query_filtered(*args, **kwargs):

      if request.method == 'GET':
        query = json.loads(request.args.to_dict().get('query'))

        filtered_query = {}

        for i in query:
          print(i, query[i])
          if i not in omit:
            print(i)
            filtered_query[i] = query[i]

        return func(filtered_query, **kwargs)
      else:
        return func(*args, **kwargs)
    return query_filtered
  return endpoint_wrapper

def jsonify_ids(result):
  if isinstance(result, list):
    for q in result:
      q['_id'] = str(q.get('_id'))
  elif isinstance(result, dict): 
    result['_id'] = str(result.get('_id'))
  return result

@app.route('/framework', methods=["GET", "POST"])
@filter_query(['framework'])
def frameworks(filtered_query=None):
  framework = mongo.db.framework

  if request.method == 'GET':

    result = jsonify_ids(list(
      framework
        .find(filtered_query)
    ))

    return jsonify(result)
  else:
    id = framework.insert(request.json)
    new_framework = framework.find_one({ '_id': id })
    jsonify_ids(new_framework)
    # new_framework['_id'] = str(new_framework.get('_id'))
    return jsonify(new_framework)

@app.route('/framework/<language>', methods=["GET"])
def get(language):
  framework = mongo.db.framework

  result = framework.find_one({'language': language})
  result = jsonify_ids(result)
  return jsonify(result)

if __name__ == '__main__':
  app.run(debug=True)