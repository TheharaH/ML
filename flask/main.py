import datetime
import os
import csv
import tkinter as tk

# Task A: Input Validation
def validate_date_input():
    """
    Prompts the user for a date in DD MM YYYY format, validates the input for:
    - Correct data type
    - Correct range for day, month, and year
    """
    while True:
        try:
            day = int(input("Please enter the day of the survey (DD): "))
            if not 1 <= day <= 31:
                print("Out of range - values must be in the range 1 to 31.")
                continue

            month = int(input("Please enter the month of the survey (MM): "))
            if not 1 <= month <= 12:
                print("Out of range - values must be in the range 1 to 12.")
                continue

            year = int(input("Please enter the year of the survey (YYYY): "))
            if not 2000 <= year <= 2024:
                print("Out of range - values must be between 2000 and 2024.")
                continue

            return f"{day:02}{month:02}{year}"
        except ValueError:
            print("Integer required. Please try again.")


def validate_continue_input():
    """
    Prompts the user to decide whether to load another dataset:
    - Validates "Y" or "N" input
    """
    while True:
        response = input("Do you want to select another dataset? (Y/N): ").strip().upper()
        if response in ["Y", "N"]:
            return response
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")


# Task B: Process CSV Data
def process_csv_data(file_path):
    """
    Processes the CSV data for the selected date and extracts:
    - Total vehicles
    - Total trucks
    - Total electric vehicles
    - Two-wheeled vehicles, and other requested metrics
    """
    outcomes = {
        "total_vehicles": 0,
        "total_trucks": 0,
        "electric_vehicles": 0,
        "two_wheeled_vehicles": 0,
        "northbound_buses": 0,
        "no_turns": 0,
        "over_speed_limit": 0,
        "junction_1_total": 0,
        "junction_2_total": 0,
        "junction_1_scooters": 0,
        "peak_hour_traffic": 0,
        "peak_hours": [],
        "rain_hours": 0,
    }

    hourly_counts_j1 = {}
    hourly_counts_j2 = {}

    try:
        with open(file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                outcomes["total_vehicles"] += 1
                if row["VehicleType"] == "Truck":
                    outcomes["total_trucks"] += 1
                if row["elctricHybrid"] == "TRUE":
                    outcomes["electric_vehicles"] += 1
                if row["VehicleType"] in ["Bike", "Motorbike", "Scooter"]:
                    outcomes["two_wheeled_vehicles"] += 1
                if row["JunctionName"] == "Elm Avenue/Rabbit Road" and row["travel_Direction_out"] == "N":
                    outcomes["northbound_buses"] += 1
                if row["travel_Direction_in"] == row["travel_Direction_out"]:
                    outcomes["no_turns"] += 1
                if int(row["VehicleSpeed"]) > int(row["JunctionSpeedLimit"]):
                    outcomes["over_speed_limit"] += 1

                junction = row["JunctionName"]
                hour = row["timeOfDay"].split(":")[0]

                if junction == "Elm Avenue/Rabbit Road":
                    outcomes["junction_1_total"] += 1
                    hourly_counts_j1[hour] = hourly_counts_j1.get(hour, 0) + 1
                    if row["VehicleType"] == "Scooter":
                        outcomes["junction_1_scooters"] += 1
                elif junction == "Hanley Highway/Westway":
                    outcomes["junction_2_total"] += 1
                    hourly_counts_j2[hour] = hourly_counts_j2.get(hour, 0) + 1

                if row["Weather_Conditions"] == "Rain":
                    outcomes["rain_hours"] += 1

        outcomes["hourly_counts_j1"] = hourly_counts_j1
        outcomes["hourly_counts_j2"] = hourly_counts_j2

        if hourly_counts_j1 or hourly_counts_j2:
            max_j1 = max(hourly_counts_j1.values(), default=0)
            max_j2 = max(hourly_counts_j2.values(), default=0)
            outcomes["peak_hour_traffic"] = max(max_j1, max_j2)
            outcomes["peak_hours"] = [
                f"Between {hour}:00 and {int(hour) + 1}:00"
                for hour, count in {**hourly_counts_j1, **hourly_counts_j2}.items()
                if count == outcomes["peak_hour_traffic"]
            ]

    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    return outcomes


def display_outcomes(outcomes, file_name):
    """
    Displays the calculated outcomes in a clear and formatted way in the IDLE shell.
    Includes all the required statistics for the selected CSV file.
    """
    print("\n" + "=" * 60)
    print(f"Results for File: {file_name}")
    print("=" * 60)
    print(f"1. Total number of vehicles: {outcomes['total_vehicles']}")
    print(f"2. Total number of trucks: {outcomes['total_trucks']}")
    print(f"3. Total number of electric vehicles: {outcomes['electric_vehicles']}")
    print(f"4. Total number of two-wheeled vehicles: {outcomes['two_wheeled_vehicles']}")
    print(f"5. Total number of buses heading north from Elm Avenue/Rabbit Road: {outcomes['northbound_buses']}")
    print(f"6. Total number of vehicles passing through both junctions without turning: {outcomes['no_turns']}")

    # Calculate and display truck percentage
    truck_percentage = (
        round((outcomes['total_trucks'] / outcomes['total_vehicles']) * 100)
        if outcomes['total_vehicles'] > 0
        else 0
    )
    print(f"7. Percentage of all vehicles that are trucks: {truck_percentage}%")

    # Calculate and display average bicycles per hour
    total_bicycles = outcomes['two_wheeled_vehicles']
    avg_bicycles_per_hour = round(total_bicycles / 24)  # Assuming a 24-hour period
    print(f"8. Average number of bicycles per hour: {avg_bicycles_per_hour}")

    print(f"9. Total number of vehicles over the speed limit: {outcomes['over_speed_limit']}")
    print(f"10. Total number of vehicles at Elm Avenue/Rabbit Road: {outcomes['junction_1_total']}")
    print(f"11. Total number of vehicles at Hanley Highway/Westway: {outcomes['junction_2_total']}")

    # Calculate and display scooter percentage
    scooter_percentage = (
        round((outcomes['junction_1_scooters'] / outcomes['junction_1_total']) * 100)
        if outcomes['junction_1_total'] > 0
        else 0
    )
    print(f"12. Percentage of vehicles at Elm Avenue/Rabbit Road that are Scooters: {scooter_percentage}%")

    print(f"13. Total vehicles in the peak hour at Hanley Highway/Westway: {outcomes['peak_hour_traffic']}")
    if outcomes["peak_hours"]:
        print(f"14. Time(s) of peak traffic hour(s): {', '.join(outcomes['peak_hours'])}")
    else:
        print(f"14. Time(s) of peak traffic hour(s): No data available")

    print(f"15. Total hours of rain: {outcomes['rain_hours']}")
    print("=" * 60 + "\n")


def save_results_to_file(outcomes, file_name="results.txt"):
    """
    Saves the processed outcomes to a text file and appends if the program loops.
    """
    try:
        with open(file_name, 'a') as file:
            for key, value in outcomes.items():
                if isinstance(value, list):
                    file.write(f"{key}: {', '.join(value)}\n")
                else:
                    file.write(f"{key}: {value}\n")
            file.write("\n")
        print(f"Results saved to {file_name}.")
    except IOError as e:
        print(f"Error saving results to file: {e}")


# Task D: Histogram Display
class HistogramApp:
    def _init_(self, traffic_data, date):
        """
        Initializes the histogram application with the traffic data and selected date.
        """
        self.traffic_data = traffic_data
        self.date = date
        self.root = tk.Tk()
        self.canvas = None

    def setup_window(self):
        """
        Sets up the Tkinter window and canvas for the histogram.
        """
        self.root.title(f"Traffic Histogram for {self.date}")
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white")
        self.canvas.pack()

    def draw_histogram(self):
        """
        Draws the histogram with axes, labels, and bars.
        """
        padding = 50
        bar_width = 20
        max_height = 400

        # Combine traffic data for scaling
        max_traffic = max(
            max(self.traffic_data["hourly_counts_j1"].values(), default=0),
            max(self.traffic_data["hourly_counts_j2"].values(), default=0)
        )

        # Draw axes
        self.canvas.create_line(padding, padding, padding, max_height + padding, width=2)  # Y-axis
        self.canvas.create_line(padding, max_height + padding, 800 - padding, max_height + padding, width=2)  # X-axis

        # Draw bars for hourly traffic
        x_pos = padding + 10
        for hour in range(24):
            hour_label = f"{hour:02d}"
            j1_count = self.traffic_data["hourly_counts_j1"].get(hour_label, 0)
            j2_count = self.traffic_data["hourly_counts_j2"].get(hour_label, 0)

            # Calculate bar heights
            j1_height = (j1_count / max_traffic) * max_height if max_traffic > 0 else 0
            j2_height = (j2_count / max_traffic) * max_height if max_traffic > 0 else 0

            # Draw bars
            self.canvas.create_rectangle(x_pos, max_height + padding - j1_height,
                                         x_pos + bar_width, max_height + padding, fill="blue")
            self.canvas.create_rectangle(x_pos + bar_width + 5, max_height + padding - j2_height,
                                         x_pos + 2 * bar_width + 5, max_height + padding, fill="red")

            # Draw hour labels
            self.canvas.create_text(x_pos + bar_width, max_height + padding + 15, text=f"{hour}:00", angle=45)

            x_pos += 2 * bar_width + 10

        # Add legend
        self.add_legend()

    def add_legend(self):
        """
        Adds a legend to the histogram to indicate which bar corresponds to which junction.
        """
        self.canvas.create_rectangle(650, 50, 670, 70, fill="blue", outline="black")
        self.canvas.create_text(680, 60, text="Elm Avenue/Rabbit Road", anchor="w")

        self.canvas.create_rectangle(650, 80, 670, 100, fill="red", outline="black")
        self.canvas.create_text(680, 90, text="Hanley Highway/Westway", anchor="w")

    def run(self):
        """
        Runs the Tkinter main loop to display the histogram.
        """
        self.setup_window()
        self.draw_histogram()
        self.root.mainloop()


# Task E: Code Loops to Handle Multiple CSV Files
class MultiCSVProcessor:
    def _init_(self, base_path=""):
        """
        Initializes the application for processing multiple CSV files.
        """
        self.current_data = None
        self.base_path = base_path

    def load_csv_file(self, file_path):
        """
        Loads a CSV file and processes its data.
        """
        try:
            return process_csv_data(file_path)
        except Exception as e:
            print(f"Error loading file: {e}")
            return None

    def clear_previous_data(self):
        """
        Clears data from the previous run to process a new dataset.
        """
        self.current_data = None

    def handle_user_interaction(self):
        """
        Handles user input for processing multiple files.
        """
        while True:
            # Step 1: Validate date input
            date = validate_date_input()
            file_name = f"traffic_data{date}.csv"
            file_path = os.path.join(self.base_path, file_name)

            if not os.path.exists(file_path):
                print(f"Error: File {file_path} not found. Please try again.")
                continue

            # Step 2: Process and display data
            self.current_data = self.load_csv_file(file_path)
            if self.current_data:
                display_outcomes(self.current_data, file_name)
                save_results_to_file(self.current_data)

                # Plot histogram
                histogram_app = HistogramApp(self.current_data, date)
                histogram_app.run()

            # Step 3: Ask user to continue or quit
            if validate_continue_input() == "N":
                print("Exiting program. Goodbye!")
                break

    def process_files(self):
        """
        Main loop for handling multiple CSV files until the user decides to quit.
        """
        print("Welcome to the Traffic Data Analysis Tool!")
        self.handle_user_interaction()


if __name__ == "_main_":
    processor = MultiCSVProcessor(base_path="")
    processor.process_files()