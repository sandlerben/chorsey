import os
import requests
import random

from app import Group, db

def update_chores():
    all_groups = Group.query.filter_by(active=True).all()
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

        smileys = [':)', ':O', ':P', 'O:)', ':D', '¯\_(ツ)_/¯']
        for member in members:
            smiley = random.choice(smileys)
            message = 'Hey {}! Your chore this week is {}. Good luck {}\n\n'.format(member.name, member.chore.name, smiley)
            message += 'Everyone else\'s chore is:'

            other_members = set(members) - set([member])
            message += ''.join(['\n\t{}: {}'.format(m.name, m.chore.name) for m in other_members])

            r = requests.post(
                'https://graph.facebook.com/v2.6/me/messages',
                params={'access_token': os.environ['facebook_access_token']},
                json={
                    'recipient': {'id': member.member_uuid},
                    'message': {'text': message}
                }
            )
            r.raise_for_status()

        group.rotation = (group.rotation + 1) % len(chores)
        db.session.add(group)
        db.session.commit()

if __name__ == '__main__':
    update_chores()
