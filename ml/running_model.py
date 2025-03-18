import pandas as pd

def format_time_diff(time_diff):
    """
    Format a timedelta object to H:M:S format without showing days.
    Converts days into hours (e.g., 1 day 00:03:35 -> 24:03:35).

    Args:
        time_diff (pd.Timedelta): The timedelta object.

    Returns:
        str: Formatted time string in H:M:S.
    """
    total_seconds = int(time_diff.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def find_min_max_timestamp_monotonic(df, target_diff=5000, tolerance=0.01):
    """
    Find the pair of timestamps with the smallest time delta where the distance
    difference between two rows is approximately equal to a target difference.
    Assumes the 'distance' column is monotonically increasing.

    Args:
        df (pd.DataFrame): DataFrame with 'distance' and 'timestamp' columns.
        target_diff (float): The target distance difference (default 5000).
        tolerance (float): Allowed deviation as a fraction of target_diff (default 0.01).

    Returns:
        tuple: (min_timestamp, max_timestamp, time_diff_hms)
    """
    # Define the tolerance range
    lower_bound = target_diff * (1 - tolerance)
    upper_bound = target_diff * (1 + tolerance)

    # Initialize variables to track the result
    min_time_delta = float('inf')
    result = (None, None)

    # Use two pointers to find the closest distance pairs
    start = 0
    for end in range(1, len(df)):
        while df['distance'][end] - df['distance'][start] > upper_bound:
            start += 1
        distance_diff = df['distance'][end] - df['distance'][start]
        if lower_bound <= distance_diff <= upper_bound:
            time_delta = abs((df['timestamp'][end] - df['timestamp'][start]).total_seconds())
            if time_delta < min_time_delta:
                min_time_delta = time_delta
                result = (df['timestamp'][start], df['timestamp'][end])

    # Calculate time difference in H:M:S format
    if result[0] and result[1]:
        time_diff = result[1] - result[0]
        time_diff_hms = str(format_time_diff(time_diff))
        return time_diff_hms, result[0], result[1],
    else:
        return None, None, None


def analyze_distances(df, target_distances, tolerance=0.01):
    """
    Analyze the DataFrame for multiple target distances.

    Args:
        df (pd.DataFrame): DataFrame with 'distance' and 'timestamp' columns.
        target_distances (dict): Dictionary where keys are labels (e.g., "400m")
                                 and values are target distances in meters.
        tolerance (float): Allowed deviation as a fraction of target_diff (default 0.01).

    Returns:
        pd.DataFrame: DataFrame summarizing the results for each target distance.
    """
    # Filter valid distances
    max_distance = df['distance'].max()
    results = []

    for label, target_diff in target_distances.items():
        if target_diff <= max_distance:
            # Call the function to find the timestamps for this distance
            time_diff_hms, min_timestamp, max_timestamp = find_min_max_timestamp_monotonic(df, target_diff, tolerance)

            # Append the result
            results.append({
                'Target Distance': label,
                'Distance (m)': target_diff,
                'Min Timestamp': min_timestamp,
                'Max Timestamp': max_timestamp,
                'Time Difference (H:M:S)': time_diff_hms
            })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    return results_df


# Target distances in meters
target_distances = {
    '400m': 400,
    '1/2 mile': 804.672,
    '1K': 1000,
    '1 mile': 1609.34,
    '2 mile': 3218.69,
    '5K': 5000,
    '10K': 10000,
    '15K': 15000,
    '10 mile': 16093.4,
    '20K': 20000,
    'Half-Marathon': 21097.5,
    '30K': 30000,
    'Marathon': 42195
}


import vdot_calculator as vdot
import datetime

def make_time(hour, minute, second):
    return datetime.time(hour=hour, minute=minute, second=second)

# Function to calculate training paces based on VDOT
def calculate_training_paces(vdot_value):
    """
    Calculate training paces (min/km) based on VDOT using Jack Daniels' method.
    """
    # Base pace in seconds per kilometer
    base_pace_sec_per_km = 3600 / (vdot_value * 0.298)  # Approximation based on Daniels' formula

    zones = {
        'Easy (E)': base_pace_sec_per_km / 0.74,
        'Marathon (M)': base_pace_sec_per_km / 0.88,
        'Threshold (T)': base_pace_sec_per_km / 0.92,
        'Interval (I)': base_pace_sec_per_km / 1.00,
        'Repetition (R)': base_pace_sec_per_km / 1.05,
    }
    # Convert paces to readable min:sec format
    zones_formatted = {
        zone: f"{int(pace // 60)}:{int(pace % 60):02d} per km"
        for zone, pace in zones.items()
    }
    return zones_formatted

# # Calculate the highest VDOT and corresponding paces
# vdot_value = 0
# distance_in_meters = None

# for i in range(len(results_df)):
#     distance = results_df.loc[i, 'Distance (m)']
#     race_time = results_df.loc[i, 'Time Difference (H:M:S)']
#     # Split the race_time string into hours, minutes, and seconds
#     hours, minutes, seconds = map(int, race_time.split(':'))
#     # Create a datetime.time object
#     race_time = make_time(hour=hours, minute=minutes, second=seconds)
#     new_vdot_value = vdot.vdot_from_time_and_distance(race_time, distance)
#     if new_vdot_value > vdot_value:
#         vdot_value = new_vdot_value
#         distance_in_meters = distance

# if distance_in_meters is not None:  # Check if distance_in_meters was assigned
#     # Use calculate_training_paces instead of vdot.paces_from_vdot
#     training_paces = calculate_training_paces(vdot_value)
#     print(f"Highest VDOT: {vdot_value:.2f} calculate from {distance_in_meters:.2f} meters")
#     print("Training Paces:")
#     for zone, pace in training_paces.items():
#         print(f"{zone}: {pace}")
# else:
#     print("No valid distances found to calculate VDOT and pace.")
