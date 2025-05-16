import matplotlib.pyplot as plt
import networkx as nx

# Define the project activities and their durations
activities = {
    'A': 2, 'B': 1, 'C': 3, 'D': 4, 'E': 2, 'F': 5, 'G': 2, 'H': 1, 'I': 2, 'J': 1, 'K': 2
}

# Define the dependencies between activities
dependencies = {
    'A': [], 'B': ['A'], 'C': ['B'], 'D': ['B'], 'E': ['B'], 'F': ['E'], 
    'G': ['C'], 'H': ['C', 'D'], 'I': ['F', 'G'], 'J': ['H', 'I'], 'K': ['J']
}

# Initialize dictionaries to store ES, EF, LS, LF, float, and drag values
nodes = {activity: {'dur': duration, 'ES': 0, 'EF': 0, 'LS': float('inf'), 'LF': float('inf'), 
                    'float': 0, 'drag': 0, 'pred': [], 'succ': [], 'CP': False} 
         for activity, duration in activities.items()}

# Add predecessors and successors based on dependencies
for activity, preds in dependencies.items():
    nodes[activity]['pred'] = preds.copy()
    for pred in preds:
        if activity not in nodes[pred]['succ']:
            nodes[pred]['succ'].append(activity)

def forward_pass():
    """Perform the forward pass to calculate ES and EF for each activity."""
    # Reset ES and EF values
    for node in nodes.values():
        node['ES'] = 0
        node['EF'] = 0
    
    processed = set()
    while len(processed) < len(nodes):
        for activity, data in nodes.items():
            if activity in processed:
                continue
            
            # Process if it's a start activity or all predecessors are processed
            if not data['pred'] or all(pred in processed for pred in data['pred']):
                if data['pred']:
                    data['ES'] = max(nodes[pred]['EF'] for pred in data['pred'])
                data['EF'] = data['ES'] + data['dur']
                processed.add(activity)

def backward_pass():
    """Perform the backward pass to calculate LS and LF for each activity."""
    # Reset LS and LF values
    for node in nodes.values():
        node['LS'] = float('inf')
        node['LF'] = float('inf')
    
    # Find project completion time
    project_duration = max(node['EF'] for node in nodes.values())
    
    # Process in reverse order
    processed = set()
    while len(processed) < len(nodes):
        for activity, data in nodes.items():
            if activity in processed:
                continue
            
            # Process if it's an end activity or all successors are processed
            if not data['succ'] or all(succ in processed for succ in data['succ']):
                if not data['succ']:
                    data['LF'] = project_duration
                else:
                    data['LF'] = min(nodes[succ]['LS'] for succ in data['succ'])
                data['LS'] = data['LF'] - data['dur']
                processed.add(activity)

def calculate_critical_path():
    """Calculate the critical path by performing forward and backward passes."""
    forward_pass()
    backward_pass()
    
    # Calculate float and identify critical path
    for activity, data in nodes.items():
        data['float'] = data['LS'] - data['ES']
        data['CP'] = abs(data['float']) < 0.0001  # Using small threshold for float comparison

def calculate_drag():
    """Calculate the drag for each activity on the critical path."""
    # Store original project duration
    forward_pass()
    backward_pass()
    original_duration = max(node['EF'] for node in nodes.values())
    
    # Calculate drag for each activity
    for activity, data in nodes.items():
        if not data['CP']:
            data['drag'] = 0
            continue
            
        # Store original duration and temporarily set to zero
        original_act_duration = data['dur']
        data['dur'] = 0
        
        # Recalculate project duration with activity duration = 0
        forward_pass()
        backward_pass()
        new_duration = max(node['EF'] for node in nodes.values())
        
        # Calculate drag
        data['drag'] = original_duration - new_duration
        
        # Restore original duration
        data['dur'] = original_act_duration
    
    # Final calculations to restore all values
    forward_pass()
    backward_pass()

def validate_dependencies(activities, dependencies):
    """Validate that all dependencies are defined correctly."""
    for activity, preds in dependencies.items():
        if activity not in activities:
            raise ValueError(f"Activity '{activity}' is not defined in activities.")
        for pred in preds:
            if pred not in activities:
                raise ValueError(f"Predecessor '{pred}' of activity '{activity}' is not defined in activities.")

# Validate dependencies before running calculations
validate_dependencies(activities, dependencies)

# Run the calculations
calculate_critical_path()
calculate_drag()

# Create visualization
G = nx.DiGraph()

# Add nodes and edges
for activity in activities:
    G.add_node(activity, duration=activities[activity])
    for pred in dependencies[activity]:
        G.add_edge(pred, activity)

# Find the critical path
critical_path = [activity for activity in activities.keys() if nodes[activity]['CP']]

# Define edge colors based on critical path
edge_colors = []
for u, v in G.edges():
    if nodes[u]['CP'] and nodes[v]['CP'] and v in nodes[u]['succ']:
        edge_colors.append('red')
    else:
        edge_colors.append('black')

# Define node colors based on critical path
node_colors = ['red' if nodes[node]['CP'] else 'lightblue' for node in G.nodes()]

# Create the visualization
plt.figure(figsize=(12, 8))
plt.margins(x=0.2, y=0.2)
pos = nx.spring_layout(G, k=1, iterations=50, seed=42)

# Draw the network
nx.draw(G, pos, 
        node_color=node_colors,
        edge_color=edge_colors,
        node_size=2000,
        with_labels=False)

# Add custom labels with duration
labels = {node: f"{node}\n{activities[node]}d" for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels, font_weight='bold')

plt.title("Project Network Diagram with Critical Path Highlighted")
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
plt.show()

# Print results table
print("\nActivity Analysis:")
print("Activity\tES\tEF\tLS\tLF\tFloat\tDrag\tCritical")
for activity in sorted(activities.keys()):
    data = nodes[activity]
    print(f"{activity}\t\t{data['ES']}\t{data['EF']}\t{data['LS']}\t{data['LF']}\t{data['float']}\t{data['drag']}\t{'Yes' if data['CP'] else 'No'}")

# Print critical path
print("\nCritical Path:", " -> ".join(critical_path))

# Print project duration
project_duration = max(node['EF'] for node in nodes.values())
print("\nProject Duration:", project_duration, "days")
