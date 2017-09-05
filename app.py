import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
db = SQLAlchemy(app)


class Group(db.Model):
    """
    A Group is a set of people and chores.
    """
    id = db.Column(db.Integer, primary_key=True)
    secret_code = db.Column(db.String(80), unique=True)
    members = db.relationship('Member', backref='group', lazy='dynamic')

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_uuid = db.Column(db.String(80), unique=True)
    name = db.Column(db.Text)
    chore = db.relationship('Chore', backref='group', lazy='dynamic')
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

class Chore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

@app.route('/health')
def health():
    return 'OK ;)'

@app.route('/messages_callback')
def messages_callback():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        verify_token = request.args.get('hub.verify_token')
        if mode == 'subscribe' and verify_token == os.environ['facebook_secret']:
            return request.args.get('hub.challenge')
        else:
            return 'Failed challenge', 403

    else:
        content = request.get_json()
        sender = content['sender']
        message_chore_assigned = 'You are all set up! Your chore for this week \
                                  is {}.'
        message_chore_unassigned = 'You are all set up! You will be assigned a \
                                    chore soon.'

        relevent_member = Member.query.filter_by(member_uuid=sender).first()
        if relevent_member and relevent_member.group is not None:
            message = message_chore_assigned.format(relevent_member.chore.name)} \
                      if relevent_member.chore else message_chore_unassigned
            requests.get(
                'https://graph.facebook.com/v2.6/me/messages',
                params={'access_token': os.environ['facebook_access_token']},
                json={
                    'recipient': {'id': sender},
                    'message': {'text': message},
                }
            )
            return 'OK'

        if not relevent_member:
            r = requests.get(
                'https://graph.facebook.com/v2.6/{}'.format(sender),
                params={
                    'fields': 'first_name',
                    'access_token': os.environ['facebook_access_token']
                },
            )
            first_name = r.json()['first_name']
            relevent_member = Member(
                member_uuid=sender,
                name=first_name,
            )
            db.session.add(relevent_member)
            db.session.commit()

        if not relevent_member.group:
            message_text = content['message']['text']
            matching_group = Group.query.filter_by(secret_code=message_text)

            if matching_group:
                relevent_member.group = matching_group
                db.session.add(relevent_member)
                db.session.commit()

                message = message_chore_assigned.format(relevent_member.chore.name)} \
                          if relevent_member.chore else message_chore_unassigned
                requests.get(
                    'https://graph.facebook.com/v2.6/me/messages',
                    params={'access_token': os.environ['facebook_access_token']},
                    json={
                        'recipient': {'id': sender},
                        'message': {'text': message},
                    }
                )

            else:
                message = 'You are almost set up! Reply with a secret group \
                           code (someone will give you this).'
                requests.get(
                    'https://graph.facebook.com/v2.6/me/messages',
                    params={'access_token': os.environ['facebook_access_token']},
                    json={
                        'recipient': {'id': sender},
                        'message': {'text': message}
                    }
                )

if __name__ == '__main__':
    app.run(debug=True)
