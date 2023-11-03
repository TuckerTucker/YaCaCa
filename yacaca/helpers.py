import uuid

def create_id():
    theID = 0
    # it seems the db doesn't handle UUIDs so we convert to int and truncate
    theID = int(uuid.uuid4()) % (2 ** 48)
    ''' 
    Limit ID to a 48-bit integer (within the range of 0 to 2^48-1).
    - create a uuid.
    - convert it to an int
    - modulo operation 
    '''
    return theID