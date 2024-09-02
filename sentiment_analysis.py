def update_polarity_subjectivity(initial_polarity, initial_subjectivity, users_dict, step_size):
    """
    Updates the initial polarity and subjectivity based on user feedback with weighted averages.

    Core users have a higher weight (3) compared to ordinary users (1).

    Parameters:
        initial_polarity (float): The initial polarity value.
        initial_subjectivity (float): The initial subjectivity value.
        users_dict (dict): Dictionary containing user types and their respective polarity and subjectivity values.
            Example:
                {
                    'core': [
                        {'polarity': 0.5, 'subjectivity': 0.6},
                        {'polarity': 0.4, 'subjectivity': 0.5},
                        ...
                    ],
                    'ordinary': [
                        {'polarity': 0.2, 'subjectivity': 0.3},
                        {'polarity': 0.1, 'subjectivity': 0.2},
                        ...
                    ]
                }
        step_size (float): The step size to control the magnitude of the update.

    Returns:
        tuple: A tuple containing the updated polarity and subjectivity.
    """

    # Define weights for each user type
    weights = {
        'core': 3,
        'ordinary': 1
    }

    weighted_polarity_sum = 0.0
    weighted_subjectivity_sum = 0.0
    total_weight = 0

    # Iterate through each user type and their corresponding user data
    for user_type, users in users_dict.items():
        weight = weights.get(user_type, 1)  # Default weight is 1 if user type is unrecognized

        for user in users:
            polarity = user.get('polarity', 0)
            subjectivity = user.get('subjectivity', 0)

            weighted_polarity_sum += polarity * weight
            weighted_subjectivity_sum += subjectivity * weight
            total_weight += weight

    # Calculate weighted averages
    if total_weight > 0:
        average_polarity = weighted_polarity_sum / total_weight
        average_subjectivity = weighted_subjectivity_sum / total_weight
    else:
        average_polarity = 0
        average_subjectivity = 0

    # Update the initial polarity and subjectivity with the weighted averages scaled by step size
    updated_polarity = initial_polarity + (step_size * average_polarity)
    updated_subjectivity = initial_subjectivity + (step_size * average_subjectivity)

    return updated_polarity, updated_subjectivity
