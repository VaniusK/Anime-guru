def find_similar_animes(name, weights, anime_encoder, df_anime, n=10, return_dist=False, neg=False):
    try:
        anime_row = df_anime[df_anime['Name'] == name].iloc[0]
        index = anime_row['anime_id']
        encoded_index = anime_encoder.transform([index])[0]
        #weights = anime_weights
        dists = np.dot(weights, weights[encoded_index])
        sorted_dists = np.argsort(dists)
        n = n + 1            
        if neg:
            closest = sorted_dists[:n]
        else:
            closest = sorted_dists[-n:]
        print('Animes closest to {}'.format(name))
        if return_dist:
            return dists, closest
        print(1)
        SimilarityArr = []
        
        for close in closest:
            decoded_id = anime_encoder.inverse_transform([close])[0]
            anime_frame = df_anime[df_anime['anime_id'] == decoded_id]
            
            anime_name = anime_frame['Name'].values[0]
            english_name = anime_frame['English name'].values[0]
            name = english_name if english_name != "UNKNOWN" else anime_name
            genre = anime_frame['Genres'].values[0]
            Synopsis = anime_frame['Synopsis'].values[0]
            similarity = dists[close]
            similarity = "{:.2f}%".format(similarity * 100)
            SimilarityArr.append({"anime_id" : decoded_id, "Name": name, "Similarity": similarity, "Genres": genre, "Synopsis":Synopsis})
        Frame = pd.DataFrame(SimilarityArr).sort_values(by="Similarity", ascending=False)
        return Frame[Frame.Name != name]
    except:
        print('{} not found in Anime list'.format(name))

def get_user_preferences(user_id, df, df_anime, plot=False, verbose=0):
    animes_watched_by_user = df[df['user_id'] == user_id]
    #print(animes_watched_by_user)
    if animes_watched_by_user.empty:
        print("User #{} has not watched any animes.".format(user_id))
        return pd.DataFrame()
    
    user_rating_percentile = np.percentile(animes_watched_by_user.rating, 75)
    animes_watched_by_user = animes_watched_by_user[animes_watched_by_user.rating >= user_rating_percentile]
    top_animes_user = (
        animes_watched_by_user.sort_values(by="rating", ascending=False)
        .anime_id.values
    )
    
    return top_animes_user

def get_rec_itoi(user_id, df_us, df_an, weights, a_enc):
    user_pref = get_user_preferences(user_id, df_us, df_an, plot=True, verbose=1)
    #list of anime_id 
    #user_pref.sort_values(by='rating', ascending=False)
    cnt = min(3, len(user_pref)) #number of prompts to i-to-i recommendation
    print(user_pref)
    res = []
    for i in range(cnt):
        anime_id = user_pref[i]
        name = df_an[df_an['anime_id'] == anime_id]["Name"]
        name = str(name).split()[1]
        rec_i = find_similar_animes(name, weights, a_enc, df_an, n = 2)
        res += list(rec_i["anime_id"].values)
    return res
