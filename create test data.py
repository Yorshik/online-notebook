import datetime

from data.folder import Folder
from data.user import User
from data.note import Note
from data.db_session import global_init, create_session

users = [
    ['Kirill', 'Chistyakov', 'kirkidzapp@gmail.com', '3113241009311313', 'Yorshik'],
    ['Vasya', 'Ivanov', 'vasya@gmail.com', '01234', 'Vasya'],
    ['Petya', 'Petrov', 'petya@gmail.com', '56789', 'Petya']
]

folders = [
    ['main', '3113', 1],
    ['second', '241009', 1],
    ['third', 'none', 1],
    ['vasya_main', 'none', 2],
    ['vasya_second', '1234', 2],
    ['vasya_third', '5678', 2],
    ['petya_main', '4321', 3],
    ['petya_second', 'none', 3],
    ['petya_third', '8765', 3]
]

notes = [
    ['note1', 1, 'none', 'no_content1'],
    ['note2', 1, '1', 'no_content2'],
    ['note3', 1, '2', 'no_content3'],
    ['note4', 2, 'none', 'no_content4'],
    ['note5', 2, '3', 'no_content5'],
    ['note6', 2, '4', 'no_content6'],
    ['note7', 3, 'none', 'no_content7'],
    ['note8', 3, '5', 'no_content8'],
    ['note9', 3, '6', 'no_content9'],
    ['note10', 4, 'none', 'no_content10'],
    ['note11', 4, '7', 'no_content11'],
    ['note12', 4, '8', 'no_content12'],
    ['note13', 5, 'none', 'no_content13'],
    ['note14', 5, '9', 'no_content14'],
    ['note15', 5, '10', 'no_content15'],
    ['note16', 6, 'none', 'no_content16'],
    ['note17', 6, '11', 'no_content17'],
    ['note18', 6, '12', 'no_content18'],
    ['note19', 7, 'none', 'no_content19'],
    ['note20', 7, '13', 'no_content20'],
    ['note21', 7, '14', 'no_content21'],
    ['note22', 8, 'none', 'no_content22'],
    ['note23', 8, '15', 'no_content23'],
    ['note24', 8, '16', 'no_content22'],
    ['note25', 9, 'none', 'no_content25'],
    ['note26', 9, '17', 'no_content26'],
    ['note27', 9, '18', 'no_content27'],
]

global_init('db/online_notebook.db')
sess = create_session()
for name, surname, email, password, nickname in users:
    user = User()
    user.name = name
    user.surname = surname
    user.email = email
    user.nickname = nickname
    user.set_password(password)
    user.modified_date = datetime.datetime.now()
    sess.add(user)

for name, password, user_id in folders:
    folder = Folder()
    folder.name = name
    folder.owner = user_id
    folder.modified_date = datetime.datetime.now()
    if password != 'none':
        folder.set_password(password)
    else:
        folder.hashed_password = 'none'
    sess.add(folder)

for name, folder_id, password, content in notes:
    note = Note()
    note.name = name
    note.the_folder = folder_id
    note.modified_date = datetime.datetime.now()
    note.content = content
    if password != 'none':
        note.set_password(password)
    else:
        note.hashed_password = 'none'
    sess.add(note)

sess.commit()
sess.close()
print('success')
