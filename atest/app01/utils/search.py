from django.db.models import Q


def q_serach(msg):
    if ',' in msg:
        msg_list = msg.strip().split(',')
    elif ' ' in msg:
        msg_list = msg.strip().split()
    else:
        msg_list = [msg]
    q = Q()
    q.connector = 'and'
    for s in msg_list:
        q.children.append(('content__icontains', s))
    return q
