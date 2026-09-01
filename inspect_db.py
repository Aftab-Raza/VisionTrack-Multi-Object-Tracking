from storage.database import DatabaseManager


def main():

    database = DatabaseManager()


    print("\n==============================")
    print("RECENT SESSIONS")
    print("==============================\n")


    sessions = (
        database.get_recent_sessions(
            limit=10
        )
    )


    for session in sessions:

        print(
            f"Session: {session['id']}"
        )

        print(
            f"Source: {session['source']}"
        )

        print(
            f"Status: {session['status']}"
        )

        print(
            f"Frames: "
            f"{session['total_frames']}"
        )

        print(
            f"IN: "
            f"{session['total_in']}"
        )

        print(
            f"OUT: "
            f"{session['total_out']}"
        )

        print(
            "------------------------------"
        )


    print("\n==============================")
    print("RECENT EVENTS")
    print("==============================\n")


    events = (
        database.get_recent_events(
            limit=20
        )
    )


    for event in events:

        print(
            f"Event #{event['id']} | "
            f"Session {event['session_id']} | "
            f"ID {event['track_id']} | "
            f"{event['event_type']} | "
            f"{event['class_name']}"
        )


    database.close()


if __name__ == "__main__":

    main()