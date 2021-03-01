def correlate_with_every_tag(df, tag_a, dict_mode = True):

    unique_tags = list(df.columns)

    # In dict_mode, the results are stored in a dict, which is good for analyzing one tag
    # However, in order to transform the data into a df later, we need a list output
    if dict_mode:
        # Loop through every tag and store the correlation in the dict
        correlation_dict = {}
        for tag_b in unique_tags:
            correlation_dict[tag_b] = correlation(df, tag_a, tag_b)
        return correlation_dict
    else:
        # Loop through every tag and store the correlation in a list
        correlation_list = []
        for tag_b in unique_tags:
            correlation_list.append(correlation(df, tag_a, tag_b))
        return correlation_list


def get_recommendations(df, tag, num_of_recommendations):

    corr_df = find_correlations(df, tag)

    recommendations_df = find_highest_correlations(corr_df, num_of_recommendations)

    print("Recommendations:", list(recommendations_df["tag"]))


def build_model():
    pass


def save_model():
    pass


def load_model():
    pass
