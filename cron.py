import os
import requests

from app import app, Group

def update_chores():
    all_groups = Group.query.all()
    for group in all_groups:
        print('Updating group {}'.format(group.secret_code))
        members = group.members
        chores = group.chores
        rotation = group.rotation

        chores_rotated = chores[rotation:] + chores[:rotation]
        for i, member in enumerate(members):
            if i == len(chores):
                break
            member.chore = chores_rotated[i]
            db.session.add(member)
        db.session.commit()

        for member in members:
            message = 'Hey {}! Your chore this week is {}. Good luck :)'.format(member.name, member.chore.name)
            r = requests.post(
                'https://graph.facebook.com/v2.6/me/messages',
                params={'access_token': os.environ['facebook_access_token']},
                json={
                    'recipient': {'id': member.member_uuid},
                    'message': {'text': message}
                }
            )
            r.raise_for_status()

        group.rotation += 1
        db.session.add(group)
        db.session.commit()

if __name__ == '__main__':
    update_chores()
