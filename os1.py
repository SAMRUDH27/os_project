import streamlit as st
import random
from collections import deque
import time
import pandas as pd
import matplotlib.pyplot as plt

class Request:
    def __init__(self, id, processing_time, priority, arrival_time):
        self.id = id
        self.processing_time = processing_time
        self.priority = priority
        self.arrival_time = arrival_time
        self.remaining_time = processing_time

    def __str__(self):
        return f"Request {self.id} (Priority: {self.priority}, Time: {self.processing_time}, Arrival: {self.arrival_time:.2f})"

class WebServer:
    def __init__(self):
        self.queue = deque()

    def add_request(self, request):
        self.queue.append(request)

    def process_round_robin(self, time_quantum):
        total_time = 0
        completed_requests = []

        while self.queue:
            current_request = self.queue.popleft()

            if current_request.remaining_time <= time_quantum:
                total_time += current_request.remaining_time
                current_request.remaining_time = 0
                completed_requests.append((current_request, total_time))
            else:
                total_time += time_quantum
                current_request.remaining_time -= time_quantum
                self.queue.append(current_request)

        return completed_requests

    def process_priority_scheduling(self, preemptive=False):
        total_time = 0
        completed_requests = []

        while self.queue:
            if preemptive:
                highest_priority = min(self.queue, key=lambda x: (x.priority, x.arrival_time))
            else:
                highest_priority = min(self.queue, key=lambda x: x.priority)

            self.queue.remove(highest_priority)
            total_time += highest_priority.processing_time
            completed_requests.append((highest_priority, total_time))

        return completed_requests

    def process_shortest_job_first(self, preemptive=False):
        total_time = 0
        completed_requests = []

        while self.queue:
            if preemptive:
                shortest_job = min(self.queue, key=lambda x: (x.remaining_time, x.arrival_time))
            else:
                shortest_job = min(self.queue, key=lambda x: x.processing_time)

            self.queue.remove(shortest_job)
            total_time += shortest_job.processing_time
            completed_requests.append((shortest_job, total_time))

        return completed_requests

def generate_requests(num_requests, max_arrival_time):
    requests = []
    for i in range(num_requests):
        processing_time = random.randint(1, 10)
        priority = random.randint(1, 5)
        arrival_time = random.uniform(0, max_arrival_time)
        requests.append(Request(i, processing_time, priority, arrival_time))
    return sorted(requests, key=lambda x: x.arrival_time)

def simulate_scheduling(requests, algorithm, time_quantum=2, preemptive=False):
    server = WebServer()
    for request in requests:
        server.add_request(request)

    start_time = time.time()
    if algorithm == "round_robin":
        completed = server.process_round_robin(time_quantum)
    elif algorithm == "priority":
        completed = server.process_priority_scheduling(preemptive=preemptive)
    elif algorithm == "sjf":
        completed = server.process_shortest_job_first(preemptive=preemptive)
    else:
        raise ValueError("Invalid scheduling algorithm")
    end_time = time.time()

    return completed, end_time - start_time

def main():
    st.title("Web Server Scheduling Simulator (Cloud Traffic Management)")

    st.sidebar.header("Simulation Parameters")
    num_requests = st.sidebar.slider("Number of Requests", 1, 100, 20)
    max_arrival_time = st.sidebar.slider("Max Arrival Time", 1.0, 100.0, 50.0)
    algorithm_choice = st.sidebar.selectbox("Select Scheduling Algorithm", ["round_robin", "priority", "sjf"])
    preemptive_choice = st.sidebar.checkbox("Enable Preemptive Scheduling")
    time_quantum = st.sidebar.slider("Time Quantum (Round Robin)", 1, 10, 2)

    if st.sidebar.button("Generate & Simulate"):
        requests = generate_requests(num_requests, max_arrival_time)
        st.session_state.requests = requests

        completed, execution_time = simulate_scheduling(
            st.session_state.requests, algorithm_choice, time_quantum, preemptive=preemptive_choice
        )

        st.header(f"{algorithm_choice.capitalize()} Scheduling Results")
        request_data = [(r.id, r.processing_time, r.priority, r.arrival_time) for r in st.session_state.requests]
        df = pd.DataFrame(request_data, columns=["ID", "Processing Time", "Priority", "Arrival Time"])
        st.dataframe(df)

        for request, completion_time in completed:
            st.write(f"{request} - Completed at: {completion_time:.2f}")

        st.write(f"Total Execution Time: {execution_time:.5f} seconds")

        fig, ax = plt.subplots()
        completion_times = [x[1] for x in completed]
        ax.plot(completion_times, label='Completion Time')
        ax.set_title("Request Completion Times")
        st.pyplot(fig)

if __name__ == "__main__":
    main()