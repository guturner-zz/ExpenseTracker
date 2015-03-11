def getMessages(user):
    from ..models import Message, User
    messages = Message.query.filter_by(uidTo=user.id).order_by(Message.time.desc()).all()
    messageSerializable = []
    for msg in messages:
        fromUser = User.query.filter_by(id=msg.uidFrom).first()
        messageSerializable.append({'id': msg.id, 'to': user.firstName, 'from': fromUser.firstName, 'memo': msg.memo, 'time': msg.time, 'isRead': msg.isRead})
    return messageSerializable

def getUnreadMessages(user, all=True):
    from ..models import Message, User

    if all:
        messages = Message.query.filter_by(uidTo=user.id, isRead=0).order_by(Message.time.desc()).all()
    else:
        messages = Message.query.filter_by(uidTo=user.id, isRead=0).order_by(Message.time.desc()).all()[0:5]

    messageSerializable = []
    for msg in messages:
        fromUser = User.query.filter_by(id=msg.uidFrom).first()
        messageSerializable.append({'id': msg.id, 'to': user.firstName, 'from': fromUser.firstName, 'memo': msg.memo, 'time': msg.time})
    return messageSerializable