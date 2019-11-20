import psycopg2
from datetime import datetime, date

#position = HOD CSE/ME/EE, DFA, ADFA, DIRECTOR

# conn = psycopg2.connect(host="127.0.0.1", user="postgres", password="inbruge137", port="5432", database="database")

conn = psycopg2.connect(host="127.0.0.1", user="postgres", password="inbruge137", port="5432", database="database")
cursor = conn.cursor()


def initialize():
    cursor.execute('''CREATE TABLE IF NOT EXISTS leaves(
                    leave_id INTEGER PRIMARY KEY,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    reason TEXT NOT NULL,
                    comments TEXT DEFAULT '',
                    status TEXT NOT NULL,
                    faculty_id INTEGER NOT NULL
                );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS borrow_leaves(
                    leave_id INTEGER PRIMARY KEY,
                    days_borrowed INTEGER NOT NULL
                );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS record_of_leaves(
                        approver TEXT NOT NULL,
                        approver_position TEXT NOT NULL,
                        approved_on DATE NOT NULL,
                        leave_id INTEGER NOT NULL
                );''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS faculty_leaves_order(
                        id INTEGER PRIMARY KEY,
                        approver_position TEXT NOT NULL
                    );''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS position_history(                    
                        faculty_id INTEGER NOT NULL, 
                        start_date DATE NOT NULL,
                        end_date DATE , 
                        position TEXT NOT NULL
                );''')    

    conn.commit()

def insert_position_history(faculty_id, position, department = None):
    if department is not None:
        position = position + ' ' + department
    cursor.execute('''INSERT INTO position_history(faculty_id, start_date, position) VALUES (%s, %s, %s)''', (faculty_id, datetime.now(), position))
    conn.commit()

def update_position_history(faculty_id, position, department = None):
    if department is not None:
        position = position + ' ' + department
    
    cursor.execute('''UPDATE position_history SET end_date = %s WHERE faculty_id = %s AND position = %s AND end_date IS NULL''', (datetime.now(), faculty_id, position))
    conn.commit()

def get_position_history():
    cursor.execute('''SELECT * FROM position_history;''')
    rows  = cursor.fetchall()
    return rows


def drop_faculty_leaves_order_table():
    cursor.execute('''DELETE FROM faculty_leaves_order;''')
    cursor.execute('''UPDATE leaves SET status = %s WHERE status LIKE %s;''',("LEAVE APPLICATION INVALIDATED","AT%"))
    conn.commit()

def get_faculty_leaves_order_table_size():
    cursor.execute('''SELECT count(*) FROM faculty_leaves_order;''')
    rows = cursor.fetchall()
    print(rows)
    return rows[0][0] 

def get_current_position_name(position_num):
    cursor.execute('''SELECT approver_position FROM faculty_leaves_order WHERE id = %s''' %(str(position_num)))
    rows = cursor.fetchall()
    return rows[0][0]

def get_current_position_num(position_name):
    print(position_name)
    # cursor.execute('''SELECT id FROM faculty_leaves_order WHERE approver_position = %s''' %(position_name))
    cursor.execute("SELECT id FROM faculty_leaves_order WHERE approver_position = %s;", [position_name])
    rows = cursor.fetchall()
    if(rows == []):
        return -1
    return rows[0][0]

def update_faculty_leaves_order_table(approver_position):
    cursor.execute('''SELECT count(*) FROM faculty_leaves_order;''')
    rows = cursor.fetchall()
    num = rows[0][0] + 1
    cursor.execute('''INSERT INTO faculty_leaves_order(id, approver_position) VALUES(%s, %s);''', (num, approver_position))
    conn.commit()

def insert_leaves_table(start_date, end_date, reason, faculty_id, status, days_borrowed=None):

    cursor.execute(
        '''SELECT * FROM leaves WHERE faculty_id = %s AND status LIKE %s''', (faculty_id, 'AT%'))

    rows = cursor.fetchall()
    # print(rows)
    if(rows != []):
        return -1

    #Get table size which will act as Leave_ID
    cursor.execute('''SELECT count(*) FROM leaves;''')
    rows = cursor.fetchall()
    #Insert in table
    cursor.execute(''' INSERT INTO leaves (leave_id, start_date, end_date, reason, comments, status, faculty_id)
                    VALUES (%s, %s, %s, %s, '', %s, %s);''', (rows[0][0] + 1, start_date, end_date, reason, status, faculty_id))

    if(days_borrowed is not None):
        cursor.execute(
            '''INSERT INTO borrow_leaves(leave_id, days_borrowed) VALUES(%s, %s);''', (rows[0][0] + 1, days_borrowed))

    conn.commit()
    return rows[0][0] + 1


def insert_trail(approver_name, leave_id, approver_position):

    cursor.execute('''INSERT INTO record_of_leaves(approver, approver_position,approved_on, leave_id) VALUES (%s, %s,%s, %s)''',
                   (approver_name, approver_position, datetime.now(), leave_id))
    conn.commit()

def add_comments(leave_id, comments):
    cursor.execute('''UPDATE leaves SET comments = %s || comments WHERE leave_id = %s;''',
                (comments, leave_id))
    conn.commit() 


def update_leave_table(status, leave_id, comments=None):
    if comments is None:
        cursor.execute('''UPDATE leaves SET status = %s WHERE leave_id = %s;''',
                       (status, leave_id))
    else:
        cursor.execute('''UPDATE leaves SET status = %s, comments = %s || comments WHERE leave_id = %s;''',
                       (status, comments, leave_id))
    conn.commit()


def delete_from_borrowed(leave_id):
    cursor.execute(
        '''DELETE FROM borrow_leaves WHERE leave_id = %s;''' % (leave_id))
    conn.commit()


def getLeavesWithStatus(status):
    cursor.execute(
        'SELECT * FROM leaves WHERE status=%s;', [status])
    rows = []
    while rows == []:
        try:
            rows = cursor.fetchall()
        except psycopg2.ProgrammingError:
            continue
        else:
            break

    return rows 

def getBorrowedLeaves(leave_id):
    cursor.execute(
        '''SELECT * FROM borrow_leaves WHERE leave_id = %s;''' % (leave_id))
    srows = cursor.fetchall()
    return srows

def getLeaveDataWithLeaveId(leave_id):
    cursor.execute(
    'SELECT * FROM leaves WHERE leave_id = %d;' % (leave_id))
    rows = cursor.fetchall()
    return rows[0]

def approve_leave(approver_name, position, department=None):
    if department is not None:
        status = 'AT ' + str(position) + ' ' + str(department)
    else:
        status = 'AT ' + str(position)
    print('status:'+status)
    list_leaves = []
    while(True):
        print("Choose 1 option: 1. View Leave Applications\n2. Approve Leave Applications\n3. Reject Leave Application\n4. Add Comments\n5. Back")
        x = int(input("Enter a number"))
        if(x == 5):
            return list_leaves

        elif(x == 4):
            leave_id_comment = int(input("Enter Leave ID of Application: "))
            comments = position + ': ' + input("Enter Comments") + '\n'
            update_leave_table(status, leave_id_comment, comments)

        elif(x == 1):
            cursor.execute('SELECT * FROM leaves WHERE status=%s', [status])
            rows = cursor.fetchall()
            for row in rows:
                cursor.execute(
                    '''SELECT * FROM borrow_leaves WHERE leave_id = %s;''' % (row[0]))
                srows = cursor.fetchall()
                if(srows != []):
                    srow = srows[0]
                    print("Leave Id: %s, Start Date: %s, End Date: %s, Reason: %s, Comments: %s, Faculty ID: %s, Days Borrowed: %s" % (
                        row[0], row[1], row[2], row[3], row[4], row[6], srow[1]))
                else:
                    print("Leave Id: %s, Start Date: %s, End Date: %s, Reason: %s, Comments: %s, Faculty ID: %s, Days Borrowed: 0" % (
                        row[0], row[1], row[2], row[3], row[4], row[6]))

        elif(x == 2):
            leave_id_approved = int(
                input("Enter Leave ID of Leave Application"))
            cursor.execute(
                'SELECT * FROM leaves WHERE leave_id = %d;' % (leave_id_approved))
            rows = cursor.fetchall()
            row = rows[0]

            # update_leave_table('APPROVED ' + status, leave_id_approved)

            approver_position = position
            if(position == 'HOD'):
                approver_position = position + ' ' + department

            insert_trail(approver_name, leave_id_approved, approver_position)

            comments = position + ': ' + input("Enter Comments if any") + '\n'
            if(position == 'HOD'):
                # insert_leaves_table(row[1], row[2], row[3], row[6], 'AT DFA')
                update_leave_table('AT DFA', leave_id_approved, comments)

            if(position == 'DIRECTOR' or position == 'DFA'):
                update_leave_table(
                    'APPROVED AT ' + position, leave_id_approved, comments)
                start_date = row[1]
                end_date = row[2]
                # s_d = date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10]))
                # e_d = date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10]))
                diff = end_date - start_date
                list_leaves.append([row[6], diff.days])
                delete_from_borrowed(leave_id_approved)

        elif(x == 3):
            leave_id_rejected = int(
                input("Enter Leave ID of Leave Application"))
            comments = position + ': ' + input("Enter Reason for Rejecting Leave") + '\n'
            update_leave_table('REJECTED ' + status,
                               leave_id_rejected, comments)
            delete_from_borrowed(leave_id_rejected)
        else:
            print("Wrong Input")


def leave_status(leave_id):

    print('LEAVE ID:' + str(leave_id))

    if str(leave_id) == 'None':
        print('inside if case---------')
        arr = {}
        return arr

    cursor.execute(
        '''SELECT * FROM leaves WHERE leave_id = %s;''' % (leave_id))
    rows = cursor.fetchall()
    print(rows)
    # print('Status: ' + rows[0][5])
    # print('Comments: ' + rows[0][4])
    # c = input("Do you want to enter any comments(y/n): ")
    # if(c == 'y'):
    #     comments = 'Faculty: ' + input('Enter Comments: ') + '\n'
    #     update_leave_table(rows[0][5], leave_id, comments)

    if len(rows) == 0:
        arr = {}
        return arr

    arr = {'status': rows[0][5],'comments':rows[0][4],'leave_id':leave_id}

    return arr


def print_leaves_table():
    cursor.execute('''SELECT * FROM leaves;''')
    rows = cursor.fetchall()
    for row in rows:
        print(row[0])


def get_trail():
    cursor.execute('''SELECT * FROM record_of_leaves''')
    rows = cursor.fetchall()
    return rows
