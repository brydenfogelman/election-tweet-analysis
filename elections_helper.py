import pymongo, pprint, time, operator
from pymongo import MongoClient
from plotly.offline import plot
from tabulate import tabulate

#-------------------#
#   MONGO HELPERS   #
#-------------------#

def setup_mongo_client(properties_file='db.properties', db_url='mongodb://%s:%s@ds161487.mlab.com:61487/election_tweets'):
    properties = dict(line.strip().split('=') 
          for line in open(properties_file)
          if not line.startswith('#') and not line.startswith('\n'))

    uri = db_url % (properties['username'], properties['password'])
    client = MongoClient(uri)
    
    return client

def get_collections(client, index_keys=[('retweeted', pymongo.ASCENDING)]):
    '''
    Creates indexes and returns the user and tweet collection. By default there is an index created for the retweeted field.
    
    Parameters:
    client - Mongo DB client
    keys - a list of (key, direction) pairs specifying the index to create
    '''
    db = client.election_tweets
    
    tweet_collection = db.tweets
    user_collection = db.users
    
    # create index for retweeted field
    tweet_collection.create_index(index_keys)
    
    return tweet_collection, user_collection

def print_mongo_results(coll, fields=None):
    for res in coll:
        # If we specified a list of fields, only take them
        if fields:
            res_fields = {}
            for k, v in res.iteritems():
                if k in fields:
                    res_fields[k] = v
            res = res_fields
        
        pprint.pprint(res)

#-------------------#
#   PLOTLY HELPER   #
#-------------------#

def get_figure(data, title, xaxis, yaxis):
    layout = dict(title=title,
                  xaxis=dict(title=xaxis),
                  yaxis=dict(title=yaxis),
                  )

    # If not a list, need to put in a list for plotly
    if not isinstance(data, list):
        data = [data]

    fig = dict(data=data, layout=layout)

    return fig


def save_plot_as_html(figure, filename):
    return plot(figure, filename=filename)


def save_plot_as_div(figure, include_plotlyjs=False, filename=None):
    div_content = plot(figure, include_plotlyjs=include_plotlyjs, output_type='div')

    # Save div to file
    if filename:
        with open(filename, 'w') as f:
            f.write(div_content)
    else:
        # Return content if not
        return div_content

#-------------------#
#   TWEET HELPERS   #
#-------------------#

def convert_datetime(twitter_time):
    '''
    Returns a time object containing the converted Twitter time.
    
    Parameters:
    twitter_time
    '''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(twitter_time,'%a %b %d %H:%M:%S +0000 %Y'))

    
#-------------------#
#   OTHER HELPERS   #
#-------------------#

def display_table(data, title=None, limit=20, **kwargs):
    '''
    Print data in table.
    '''
    if title:            
        print title + ' (limited to %s results)' % limit
    if type(data[0]) == tuple:
        data = [[str(tup[0]), str(tup[1])] for tup in data[:limit]]
    print tabulate(data[:limit], tablefmt="fancy_grid", **kwargs)
    print '\n'
    
def get_dict_representation(X, feature_names, merge=False):
    '''
    Convert sparse matrix representation to dictionary.
    '''
    dict_vectorizer = DictVectorizer()

    # set feature names so dictionaries can be unpacked
    dict_vectorizer.feature_names_ = feature_names

    # merge dictionaries
    if merge:
        return merge_dicts(*dict_vectorizer.inverse_transform(X))
    # keep seperate
    else:
        return dict_vectorizer.inverse_transform(X)
    
def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def sort_dict(d, reverse=True):
    return sorted(d.items(), key=operator.itemgetter(1), reverse=reverse)


