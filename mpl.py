import time
import random
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display, clear_output

# Generate some sample data
def get_data():
    return {
        'time': time.time(),
        'value1': random.uniform(0, 100),
        'value2': random.uniform(0, 100),
        'value3': random.uniform(0, 100)
    }

# Create a figure and axes for the plot
fig, ax = plt.subplots(figsize=(12, 6))

# Create a dataframe to store the data
df = pd.DataFrame(columns=['time', 'value1', 'value2', 'value3'])

# Function to update the plot and table
def update_visualization():
    global df
    
    # Get new data
    new_data = get_data()
    
    # Add new data to the dataframe
    df = df.append(new_data, ignore_index=True)
    
    # Clear the previous plot
    ax.clear()
    
    # Plot the data
    ax.plot(df['time'], df['value1'], label='Value 1')
    ax.plot(df['time'], df['value2'], label='Value 2')
    ax.plot(df['time'], df['value3'], label='Value 3')
    ax.set_title('Real-Time Data Visualization')
    ax.set_xlabel('Time')
    ax.set_ylabel('Value')
    ax.legend()
    
    # Display the updated plot
    plt.draw()
    plt.pause(0.001)
    
    # Display the updated table
    clear_output(wait=True)
    display(df)

# Run the update function in a loop
while True:
    update_visualization()
    time.sleep(1)
