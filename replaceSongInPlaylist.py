import zmq
import csv

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:8000")

while True:
    #  Wait for next request from client
    message = socket.recv()
    stringMessage = message.decode("utf-8")
    messageSplit = stringMessage.split(':')

    # Read spreadsheet
    filename = "playlists.csv"
    with open(filename, "r+") as playlists:
        datareader = csv.reader(playlists)
        data = list(datareader)

    # Modify Spreadsheet
    print(data)
    for row in data[1:]:
        if row[0] == messageSplit[0]:
            if row[1] == messageSplit[1]:
                row[1] = messageSplit[2]
    print(data)

    # Save Changes
    with open("playlists.csv", "w", newline='') as playlists:
        datawriter = csv.writer(playlists)
        for row in data:
            datawriter.writerow(row)



    #  Send reply back to client
    socket.send(b"Complete")