import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Logarithmic fatigue-adjusted CP model
def fatigue_log_cp_model(time, cp, w_prime, k, alpha, F):
    return cp + (w_prime / ((time + k) ** alpha)) - F * np.log(time + 1)

def predict_long_duration_power(short_durations, short_power, long_durations_to_predict, cp20):
    short_durations_seconds = np.array(short_durations) * 60
    long_durations_seconds = np.array(long_durations_to_predict) * 60
    short_power_array = np.array(short_power)

    # Set a more conservative CP guess
    initial_cp = 0.95 * cp20  # Start CP at ~98% of 60-min power
    initial_w_prime = (short_power_array[0] - initial_cp) * short_durations_seconds[0]
    initial_k = 300  # Mid-range offset
    initial_alpha = 1.0  # Decay exponent
    initial_F = 10.0  # Start with moderate fatigue effect

    # Set conservative bounds to prevent issues
    bounds = ([cp20 * 0.85,  # CP lower bound (~85% of 60-min power)
               2000,  # W' lower bound (minimum viable energy store)
               10,    # k min (prevent singularity)
               0.5,   # alpha min (prevent unrealistic power retention)
               1.0],  # F min (force fatigue effect)
              [cp20 * .98,  # CP upper bound (5% above 60-min power)
               20000,  # W' upper bound (realistic athlete range)
               3000,   # k max (prevent excessive delay in fatigue onset)
               2.0,    # alpha max (prevent over-aggressive decay)
               20.0])  # F max (limit extreme fatigue effects)

    # Ensure initial conditions are inside bounds
    p0 = np.clip([initial_cp, initial_w_prime, initial_k, initial_alpha, initial_F],
                 bounds[0], bounds[1])

    popt, _ = curve_fit(
        fatigue_log_cp_model,
        short_durations_seconds,
        short_power_array,
        p0=p0,
        bounds=bounds,
        maxfev=10000
    )

    cp, w_prime, k, alpha, F = popt
    predicted_power = fatigue_log_cp_model(long_durations_seconds, cp, w_prime, k, alpha, F)

    return predicted_power, cp, w_prime, k, alpha, F

cp20 = 332
short_durations_minutes = [1, 5, 10, 20, 30, 60,90,120]
short_power_watts = [435, 388, 332, 328, 270, 244, 241,232]  # Example power data
long_durations_minutes_to_predict = [120, 150, 300]

predicted_power_watts, fitted_cp, fitted_w_prime, fitted_k, fitted_alpha, fitted_F = predict_long_duration_power(
    short_durations_minutes, short_power_watts, long_durations_minutes_to_predict, cp20
)

print(f"Predicted power for 120 minutes: {predicted_power_watts[0]:.2f} watts")
print(f"Predicted power for 300 minutes: {predicted_power_watts[1]:.2f} watts")
print(f"Fitted Critical Power (CP): {fitted_cp:.2f} watts")
print(f"Fitted W' (W prime): {fitted_w_prime:.2f} Joules")
print(f"Fitted k (offset factor): {fitted_k:.2f}")
print(f"Fitted alpha (decay exponent): {fitted_alpha:.2f}")
print(f"Fitted F (fatigue factor): {fitted_F:.2f}")

all_durations_minutes = short_durations_minutes + long_durations_minutes_to_predict
all_durations_seconds = np.array(all_durations_minutes) * 60
all_power_watts = short_power_watts + list(predicted_power_watts)

plt.figure(figsize=(10,6))
plt.scatter(short_durations_minutes, short_power_watts, label="Measured Data", color='blue')
plt.scatter(long_durations_minutes_to_predict, predicted_power_watts, label="Predicted Data", color='red')
plt.plot(all_durations_minutes, fatigue_log_cp_model(np.array(all_durations_minutes)*60, fitted_cp, fitted_w_prime, fitted_k, fitted_alpha, fitted_F), label="Fitted Curve", linestyle="dashed", color="black")
plt.xlabel("Duration (minutes)")
plt.ylabel("Power (watts)")
plt.title("Tanner -> Power-Duration Curve Prediction (Fatigue-Log Model)")
plt.legend()
plt.grid(True)
plt.show()


def peak_avg_wattage(df, time_window):
    """
    Calculate the peak average wattage over a specified time window.

    Args:
    df (pd.DataFrame): The dataframe containing time series power data.
    time_window (int): The time window in seconds over which to calculate the average power.

    Returns:
    float: The maximum average power found in the dataset over the specified time window.
    """
    # Ensure 'watts' column has no NaNs
    df['watts'] = df['watts'].fillna(0)

    # Compute the rolling average power over the specified time window
    df['rolling_avg'] = df['watts'].rolling(window=time_window, min_periods=1).mean()

    # Find the peak (maximum) average power
    peak_avg_wattage = df['rolling_avg'].max()

    return peak_avg_wattage

def evaluate_peak_avg_wattages(df, time_windows):
    """
    Evaluate the peak average wattage for multiple time windows if the dataset's duration allows.

    Args:
    df (pd.DataFrame): The dataframe containing time series power data.
    time_windows (list of int): List of time windows (in seconds) to evaluate.

    Returns:
    pd.DataFrame: A dataframe with the results for each valid time window.
    """
    # Get the total duration of the dataset
    total_time = df["time"].max() - df["time"].min()

    # Evaluate peak average wattage for valid time windows
    results = {}
    for time_window in time_windows:
        if total_time >= time_window:
            results[time_window] = peak_avg_wattage(df, time_window)
        else:
            results[time_window] = None

    # Convert results to a DataFrame
    results_df = pd.DataFrame(list(results.items()), columns=["Time Window (s)", "Peak Average Wattage (W)"])
    
    return results_df

# # Define the time windows to evaluate
# time_windows = [5, 60, 300, 600, 1200, 3600, 7200, 10800, 14400, 18000]

# # Call the function and display results
# results_df = evaluate_peak_avg_wattages(df, time_windows)
# print(results_df)


import pandas as pd
import numpy as np

def cycling_normalized_power(power):
    """
    Calculates normalized power (np) and average power for cycling data.

    Args:
        power (list or pd.Series): A list or pandas Series of power values (watts).

    Returns:
        tuple: A tuple containing (normalized power, average power).
               Returns (None, None) if the input is invalid or if there are insufficient data points.
    """
    if not isinstance(power, (list, pd.Series)):
        return None, None

    if isinstance(power, list):
        number_series = pd.Series(power)
    else:
        number_series = power.copy()

    number_series = number_series.dropna()

    if len(number_series) < 30:
        return None, None

    window_size = 30
    windows = number_series.rolling(window_size)
    power_30s = windows.mean().dropna()

    if len(power_30s) == 0:
        return None, None

    average_power = round(power_30s.mean(), 0)

    normalized_power = round((((power_30s**4).mean())**0.25), 0)

    return normalized_power, average_power

# Example usage
# power_data = [100, 120, 150, 1130, 110, 180, 200, 190, 170, 160,
#               155, 165, 175, 185, 195, 205, 215, 225, 235, 245,
#               240, 230, 220, 210, 200, 195, 185, 175, np.nan,165, 155,
#               150, 160, 170, 180, 190, 2000, 2100, 220, 230, 240,100, 120, 150, 1130, 110, 180, 200, 190, 170, 160,
#               155, 165, 175, 185, 195, 205, 215, 225, 235, 245,
#               240, 230, 220, 210, 200, 195, 185, 175, 165, 155,
#               150, 160, 170, 180, 190, 2000, 2100, 220, 230, 240,np.nan,np.nan]

# np_result, avg_result = cycling_normalized_power(power_data)
# print(f"Normalized power (np): {np_result}")
# print(f"Average power: {avg_result}")
