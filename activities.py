import json, random


def open_json(filename): # Opens file as json
    with open(filename) as f:
        topics = json.load(f)
        return topics


def write_json(filename, json_file): # Writes json
    with open(filename, "w"):
        json.dump(json_file, indent=4)
        

def get_random_activity(selected_topics):
    '''gets a random activity from one of the selected topics'''
    topics = open_json("topics.json")
    random_topic = random.choice(selected_topics)
    random_activity = random.choice(topics[random_topic])
    return random_topic, random_activity


# # Chooses a random activity from the entered topic 
# def get_random_activity(selected_topics): 
#     topics = open_json("topics.json")
#     num_activities = 0
#     for topic in selected_topics: # Calculates number of total activities
#         num_activities += len(topics[topic])
#     random_number = random.randrange(1, num_activities + 1, 1) # Generates random activity number
#     checked_activities = 0 # Number of activities that have already been checked
#     for topic in selected_topics: # Finds the topic that contains the selected activity
#         for activity in topics[topic]:# Filters activities by topics
#             if activity["id"] + checked_activities == random_number: # If the activity is the selected activity ...
#                 print("ID:", activity["id"], "\nName:", activity["name"], "\nDescription:", activity["description"]) # Prints random activity
#         checked_activities += len(topics[topic]) # Adds the number of activities tested


def get_all_topics():
    topics = open_json("topics.json")
    return set(topics.keys())


selected_topics = ["Running", "Meditation", "Walking"] # Topics to filter, first letter MUST be capital
def main():
    y, x = get_random_activity(selected_topics) # Topics to filter, MUST be non empty list
    print(x.get("name"), x.get("description"))

if __name__ == "__main__":
    main()