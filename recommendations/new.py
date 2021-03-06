import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import random




# Load data from disk
def ratings_reader():
   names = ['user_id', 'item_id', 'rating', 'timestamp']
   df = pd.read_csv('dataset/u.data', sep='\t', names=names)
   n_users = df.user_id.unique().shape[0]
   n_items = df.item_id.unique().shape[0]

   # Create r_{ui}, our ratings matrix
   ratings = np.zeros((n_users, n_items))
   for row in df.itertuples():
       ratings[row[1]-1, row[2]-1] = row[3]

   return ratings

ratings = ratings_reader()
n_users = ratings.shape[0]
n_items = ratings.shape[1]




def test_train_split(ratings):
   test = np.zeros(ratings.shape)
   train = ratings.copy()

   for user in range(ratings.shape[0]):
      test_ratings = np.random.choice(ratings[user, :].nonzero()[0],
      size = 10, replace=False)

      train[user, test_ratings] = 0
      test[user, test_ratings] = ratings[user, test_ratings]

   assert(np.all((train * test) == 0))

   return train, test


train, test = test_train_split(ratings)



def get_rmse(actual, pred):
   pred = pred[actual.nonzero()].flatten()
   actual = actual[actual.nonzero()].flatten()
   mse = mean_squared_error(pred, actual)
   return mse**0.5


n_iters = 200
gamma = 0.001
lmbda = 0.01

k = 80

users, items = train.nonzero()

Bu = np.zeros(n_users)
Bi = np.zeros(n_items)
P = np.random.rand(n_users, k)
Q = np.random.rand(n_items, k)
global_bias = np.mean(train[np.where(train != 0)])
train_rmses = []
test_rmses = []


def trainer(n_iters, users, items, P, Q, Bu, Bi, global_bias, trainer, tester, gamma, lmbda):
   # use the stochastic gradient descent approach to mimimize the error in prediction
   train_rmses = []
   test_rmses = []

   for n in range(n_iters):
      for u,i in zip(users, items):
         prediction = P[u,:].dot(Q[i,:].T) + Bu[u] + Bi[i] + global_bias
         e = train[u,i] - prediction
         Bu[u] += gamma * (e - lmbda * Bu[u])
         Bi[i] += gamma * (e - lmbda * Bi[i])
         P[u,:] += gamma * (e * Q[i,:] - lmbda * P[u,:])
         Q[i,:] += gamma * (e * P[u,:] - lmbda * Q[i,:])
      
      pred = np.zeros((P.shape[0], Q.shape[0]))

      for u in range(P.shape[0]):
         for i in range(Q.shape[0]):
            pred[u,i] = P[u,:].dot(Q[i,:].T) + Bu[u] + Bi[i] + global_bias

       

      train_rmse = get_rmse(train, pred)
      test_rmse = get_rmse(test, pred)
      train_rmses.append(train_rmse)
      test_rmses.append(test_rmse)
      print(n+1, train_rmse, test_rmse)
      return(train_rmses, test_rmses)


# add the below line to start the training
# train_rmses, test_rmses = trainer(n_iters, users, items, P, Q, Bu, Bi, global_bias, train, test, gamma, lmbda)




def draw_learning_curve(n_iters, train_rmse, test_rmse):
   # use this function to use the above train_rmses and test_rmses to plot the rmse curves, 
   # see how they converge
   plt.plot(range(n_iters), train_rmse, label = 'Train', linewidth = 5)
   plt.plot(range(n_iters), test_rmse, label = 'Test', linewidth = 5)
   plt.xlabel('Iterations')
   plt.ylabel('RMSE')
   plt.legend(loc='best', fontsize=30)


def cosine_similarity(Q):
   # finds the cosine similarity based on item feature matrix
   # parameter: Q ( item latent feature matrix)
   sim = Q.dot(Q.T)
   norms = np.array([np.sqrt(np.diagonal(sim))])
   return sim/ norms/ norms.T


def get_top_k(sims, movie_id, k):
   # return the tuple of top k movies using the similarity matrix and movie_id
   movie_indices = np.argsort(sims[movie_id,:])[::-1]
   top_k = movie_indices[1:k]   
   top_k = tuple(top_k)
   return top_k
