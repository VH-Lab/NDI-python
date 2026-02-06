import json
import os
from ndi.common.path_constants import PathConstants

def stimulus_temporal_frequency(stimulus_parameters):
    """
    Calculates the temporal frequency of a visual stimulus.

    TF_VALUE, TF_NAME = STIMULUSTEMPORALFREQUENCY(STIMULUS_PARAMETERS)

    This function attempts to determine the temporal frequency (in Hz) of a
    visual stimulus by examining its parameters (`STIMULUS_PARAMETERS`) and
    applying rules defined in an external JSON configuration file
    (`ndi_stimulusparameters2temporalfrequency.json`).

    If no known temporal frequency parameter field name is found within
    STIMULUS_PARAMETERS after checking all rules, TF_VALUE is returned as None
    and TF_NAME is returned as an empty string (`''`).

    Args:
        stimulus_parameters (dict): A dictionary where each key represents a parameter of the stimulus.

    Returns:
        tuple: (tf_value, tf_name)
            tf_value (float or None): The calculated temporal frequency, typically in Hz.
            tf_name (str): The field name in STIMULUS_PARAMETERS from which TF_VALUE was derived.
    """
    tf_value = None
    tf_name = ''

    # Construct file path safely
    json_file_path = os.path.join(PathConstants.common_folder(), 'stimulus', 'ndi_stimulusparameters2temporalfrequency.json')

    # Check if JSON file exists before trying to read
    if not os.path.exists(json_file_path):
        raise FileNotFoundError(f"JSON configuration file not found at: {json_file_path}")

    try:
        with open(json_file_path, 'r') as f:
            ndi_stim_tf_info = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Error reading or decoding JSON file: {json_file_path}\n{e}")

    for rule in ndi_stim_tf_info:
        # Check if the current rule object has the necessary fields
        required_fields = {'parameter_name', 'temporalFrequencyMultiplier', 'temporalFrequencyAdder', 'isPeriod', 'parameterMultiplier'}
        if not all(field in rule for field in required_fields):
             raise ValueError(f"JSON entry is missing required fields: {required_fields}")

        current_param_name = rule['parameter_name']

        # Check if the parameter exists in the input structure
        if current_param_name in stimulus_parameters:
            # Process the match
            try: # Catch calculation errors for this specific rule
                original_value = stimulus_parameters[current_param_name]

                # Ensure value is numeric before calculations
                if not isinstance(original_value, (int, float)):
                   raise ValueError(f"Parameter '{current_param_name}' must have a numeric scalar value.")

                tf_value = rule['temporalFrequencyAdder'] + rule['temporalFrequencyMultiplier'] * original_value

                if rule['isPeriod']:
                    # Add check for zero to avoid division by zero error
                    if tf_value == 0:
                        raise ValueError(f"Temporal period value for parameter '{current_param_name}' results in zero after transformation; cannot divide by zero.")
                    tf_value = 1.0 / tf_value

                if rule['parameterMultiplier']:
                    multiplier_param_name = rule['parameterMultiplier']
                    # Check if the multiplier parameter exists
                    if multiplier_param_name in stimulus_parameters:
                        tf_mult_parm_value = stimulus_parameters[multiplier_param_name]

                        # Ensure multiplier value is numeric and scalar
                        if not isinstance(tf_mult_parm_value, (int, float)):
                             raise ValueError(f"Parameter multiplier '{multiplier_param_name}' must have a numeric scalar value.")
                        else:
                             tf_value = tf_value * tf_mult_parm_value
                    else:
                        raise ValueError(f"Required parameter multiplier field '{multiplier_param_name}' not found in stimulus_parameters.")

                tf_name = current_param_name
                return tf_value, tf_name # Return as soon as the first match is successfully processed

            except Exception as e: # Catch errors specific to calculations for THIS rule
                 # Throw a new error providing context about which rule failed
                 raise RuntimeError(f"Error during TF calculation for parameter rule '{current_param_name}': {e}")

    return tf_value, tf_name
