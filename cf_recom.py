from imports import *

def RecommenderNet(num_users, num_animes, embedding_size=128):
    # User input layer and embedding layer
    user = Input(name='user_encoded', shape=[1])
    user_embedding = Embedding(name='user_embedding', input_dim=num_users, output_dim=embedding_size)(user)
    
    # Anime input layer and embedding layer
    anime = Input(name='anime_encoded', shape=[1])
    anime_embedding = Embedding(name='anime_embedding', input_dim=num_animes, output_dim=embedding_size)(anime)
    
    # Dot product of user and anime embeddings
    dot_product = Dot(name='dot_product', normalize=True, axes=2)([user_embedding, anime_embedding])
    flattened = Flatten()(dot_product)
    
    # Dense layers for prediction
    dense = Dense(64, activation='relu')(flattened)
    output = Dense(1, activation='sigmoid')(dense)
    
    # Create and compile the model
    model = Model(inputs=[user, anime], outputs=output)
    model.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=["mae", "mse"])
    
    return model

def extract_weights(name, model):
    # Get the layer by name from the model
    weight_layer = model.get_layer(name)
    
    # Get the weights from the layer
    weights = weight_layer.get_weights()[0]
    
    # Normalize the weights
    weights = weights / np.linalg.norm(weights, axis=1).reshape((-1, 1))
    
    return weights

def find_similar_users(item_input, user_encoder,  user_weights, n=10, return_dist=False, neg=False):
    try:
        index = item_input
        encoded_index = user_encoder.transform([index])[0]
        weights = user_weights
        dists = np.dot(weights, weights[encoded_index])
        sorted_dists = np.argsort(dists)
        n = n + 1
        
        if neg:
            closest = sorted_dists[:n]
        else:
            closest = sorted_dists[-n:]
            
        SimilarityArr = []
        
        for close in closest:
            similarity = dists[close]
            if isinstance(item_input, int):
                decoded_id = user_encoder.inverse_transform([close])[0]
                SimilarityArr.append({"similar_users": decoded_id, "similarity": similarity})
        Frame = pd.DataFrame(SimilarityArr).sort_values(by="similarity", ascending=False)
        return Frame
    except:
        print('\033[1m{}\033[0m, Not Found in User list'.format(item_input))

def get_user_preferences(user_id, df, df_anime, plot=False, verbose=0):
    animes_watched_by_user = df[df['user_id'] == user_id]
    
    if animes_watched_by_user.empty:
        print("User #{} has not watched any animes.".format(user_id))
        return pd.DataFrame()
    
    user_rating_percentile = np.percentile(animes_watched_by_user.rating, 75)
    animes_watched_by_user = animes_watched_by_user[animes_watched_by_user.rating >= user_rating_percentile]
    top_animes_user = (
        animes_watched_by_user.sort_values(by="rating", ascending=False)
        .anime_id.values
    )
    
    anime_df_rows = df_anime[df_anime["anime_id"].isin(top_animes_user)]
    anime_df_rows = anime_df_rows[["Name", "Genres"]]
    
    if verbose != 0:
        print("User \033[1m{}\033[0m has watched {} anime(s) with an average rating of {:.1f}/10\n".format(
            user_id, len(animes_watched_by_user), animes_watched_by_user['rating'].mean()
        ))
        print('\033[1m----- Preferred genres----- \033[0m\n')

    if plot:
        genres_list = []
        for genres in anime_df_rows['Genres']:
            if isinstance(genres, str):
                for genre in genres.split(','):
                    genres_list.append(genre.strip())

        #showWordCloud(dict(Counter(genres_list)))
    
    return anime_df_rows

def get_recommended_animes(similar_users, user_pref, df, df_anime, n=10):
    recommended_animes = []
    anime_list = []
    
    for user_id in similar_users.similar_users.values:
        pref_list = get_user_preferences(int(user_id), df, df_anime)
        if not pref_list.empty:  # Check if user has watched any animes
            pref_list = pref_list[~pref_list["Name"].isin(user_pref["Name"].values)]
            anime_list.append(pref_list.Name.values)
            
    if len(anime_list) == 0:
        print("No anime recommendations available for the given users.")
        return pd.DataFrame()
    
    anime_list = pd.DataFrame(anime_list)
    sorted_list = pd.DataFrame(pd.Series(anime_list.values.ravel()).value_counts()).head(n)
    # Count the occurrences of each anime in the entire dataset
    anime_count = df['anime_id'].value_counts()
    
    for i, anime_name in enumerate(sorted_list.index):
        if isinstance(anime_name, str):
            try:
                anime_id = df_anime[df_anime.Name == anime_name].anime_id.values[0]
                english_name = df_anime[df_anime['Name'] == anime_name]['English name'].values[0]
                name = english_name if english_name != "UNKNOWN" else anime_name
                genre = df_anime[df_anime.Name == anime_name].Genres.values[0]
                Synopsis = df_anime[df_anime.Name == anime_name].Synopsis.values[0]
                n_user_pref = anime_count.get(anime_id, 0)  # Get the total count of users who have watched this anime
                recommended_animes.append({
                    "anime_id" : anime_id,
                    "n": n_user_pref,
                    "anime_name": anime_name, 
                    "Genres": genre, 
                    "Synopsis": Synopsis
                })
            except:
                pass
    return pd.DataFrame(recommended_animes)

def cf_get_rec(user_id, df_us, df_an, path_model):
    df = df_us
    scaler = MinMaxScaler(feature_range=(0, 1))

    # Scale the 'score' column between 0 and 1
    df['scaled_score'] = scaler.fit_transform(df[['rating']])
    # Encoding categorical data

    ## Encoding user IDs
    user_encoder = LabelEncoder()
    df["user_encoded"] = user_encoder.fit_transform(df["user_id"])
    num_users = len(user_encoder.classes_)

    ## Encoding anime IDs
    anime_encoder = LabelEncoder()
    df["anime_encoded"] = anime_encoder.fit_transform(df["anime_id"])
    num_animes = len(anime_encoder.classes_)

    model = RecommenderNet(num_users, num_animes)
    model.load_weights(path_model)

    # Printing dataset information
    print("Number of unique users: {}, Number of unique anime: {}".format(num_users, num_animes))
    print("Minimum rating: {}, Maximum rating: {}".format(min(df['rating']), max(df['rating']))) 
    
    # Extract weights for anime embeddings
    anime_weights = extract_weights('anime_embedding', model)
    # Extract weights for user embeddings
    user_weights = extract_weights('user_embedding', model)
    df_anime = df_an
    popularity_threshold = 50
    df_anime= df_anime.query('Members >= @popularity_threshold')
    
    random_user = user_id
    # Find similar users to the random user
    similar_users = find_similar_users(random_user, user_encoder,  user_weights, n=10, neg=False)
    print(similar_users)
    similar_users = similar_users[similar_users.similarity > 0.4]
    similar_users = similar_users[similar_users.similar_users != random_user]

    user_pref = get_user_preferences(random_user, df_us, df_an, plot=True, verbose=1)

    # Get recommended animes for the random user
    recommended_animes = get_recommended_animes(similar_users, user_pref, df_us, df_an, n=10)
    
    print('\n> Top recommendations for user: {}'.format(random_user))
    return recommended_animes