"""
Given an string in base64, decode it following this steps:

1. Make sure the string has a valid length (multiple of 2)
2. Read the pairs of characters
2.1 If the first character is a tilde "~", the second character will be the key to the following values
2.2 If not, just decode according to the base64 alphabet, reverting the offset and multiplying according to the key
3. Assign the values to the key's list in the dictionary 

BASE64 ALPHABET: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_

KEYS:
    P: Pressure sensor array -> offset = 0, multiplier = 1
    I: IMU array -> offset = 180.0, multiplier = 0.1
    D: Distance sensor array (L4) -> offset = 0, multiplier = 1
    M: Matrix distance sensor array (L5) -> offset = 0, multiplier = 1
"""

BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

# Define a dictionary with the keys and the offsets and multipliers
keys = {
    "P": [0, 1],
    "I": [180.0, 10],
    "D": [0, 1],
    "M": [0, 1]
}


def combine_pair_base64(pair):
    """
    Combine a pair of characters according to the base64 alphabet

    :param pair: the pair of characters to be combined
    :return: the combined value
    """
    # Find the indexes of the characters in the base64 alphabet
    MSB = BASE64_ALPHABET.index(pair[0])
    LSB = BASE64_ALPHABET.index(pair[1])

    # Combine the two 6-bit values to get the original 12-bit value
    combined_value = (MSB << 6) | LSB

    # Assert that the combined value is in the range (0-4095)
    assert 0 <= combined_value <= 4095

    return combined_value


def decode_base64(encoded_string):
    """
    Decode a base64 string

    :param encoded_string: the string to be decoded
    :return: the decoded values
    """

    # Check if the string has a valid length
    if len(encoded_string) % 2 != 0:
        print("Invalid string length")
        return

    # Define an dictionary to store the decoded values
    decoded_values = {}
    dict_key = ""

    # Iterate over each pair of characters in the string
    for i in range(0, len(encoded_string), 2):

        # Get the pair of characters
        pair = encoded_string[i:i+2]

        # Check if the first character is a tilde
        if pair[0] == "~":

            # Get the key
            dict_key = pair[1]

        else:

            # Get the offset and multiplier
            offset = keys[dict_key][0]
            multiplier = keys[dict_key][1]

            # Decode the pair of characters
            combined_value = combine_pair_base64(pair)

            # The following equation is used to encode the data: ((input + offset) * multiplier)
            # So, to decode the data, we need to revert the equation: (input / multiplier) - offset
            decoded_value = (combined_value / multiplier) - offset

            # Append the decoded value to the dictionary key's list
            if dict_key in decoded_values:
                decoded_values[dict_key].append(decoded_value)
            else:
                decoded_values[dict_key] = [decoded_value]

    return decoded_values
