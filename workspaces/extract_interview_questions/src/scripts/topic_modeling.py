import pandas as pd  # type: ignore
from bertopic import BERTopic  # type: ignore
import json

# Load the dataset from the JSON file
df = pd.read_json("results/merged_20250223_210238.json")

# Combine the 'question' and 'answer' columns into one text column for topic modeling
df["text"] = df["question"] + " " + df["answer"]

# Create and fit the BERTopic model
topic_model = BERTopic(language="english", calculate_probabilities=True)
topics, _ = topic_model.fit_transform(df["text"])

# Add the predicted topics to the DataFrame
df["bertopic_labeled_topic"] = topics

# Extract topic information and prepare a dictionary of topic details
topic_info = topic_model.get_topic_info()
all_topics = {}

for topic_id in topic_info["Topic"]:
    if topic_id == -1:  # Skip outliers
        continue

    python_topic_id = int(topic_id)
    words = topic_model.get_topic(python_topic_id)
    count = topic_info[topic_info["Topic"] == topic_id]["Count"].values[0]

    # Convert words (list of tuples) to a list of lists with native types
    converted_words = [[word, float(weight)] for word, weight in words]

    all_topics[python_topic_id] = {"size": int(count), "words": converted_words}

    print(f"Topic {python_topic_id}: {int(count)} documents")
    print(f"Words: {converted_words}")

# Save the topic details to a JSON file
with open("results/topic_details.json", "w") as f:
    json.dump(all_topics, f, indent=4)
print("Topic details saved to results/topic_details.json")

# Create a mapping from topic ID to the list of keywords (extracting only the words)
topic_keywords = {
    topic_id: [word for word, _ in topic_model.get_topic(topic_id)]
    for topic_id in all_topics.keys()
}

# Add a new 'keywords' column to the DataFrame based on the labeled topics
df["keywords"] = df["bertopic_labeled_topic"].apply(lambda t: topic_keywords.get(t, []))

# Print a subset of the DataFrame to inspect the 'answer', 'labeled_topic', and 'keywords' columns
print(df[["answer", "bertopic_labeled_topic", "keywords"]])

# Save the updated DataFrame with the new 'keywords' column to a JSON file
output_path = "results/labeled_interview_qa_bertopic.json"
df.to_json(output_path, orient="records", indent=4)
print(f"Labeled dataset with keywords saved to {output_path}")
