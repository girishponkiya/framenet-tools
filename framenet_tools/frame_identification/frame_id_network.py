import torch
import torch.nn as nn
from torch.autograd import Variable

hidden_size = 2048
hidden_size2 = 1024
num_epochs = 5
learning_rate = 0.001
embedding_size = 300

class Net(nn.Module):
        def __init__(self, embedding_size, hidden_size, hidden_size2, num_classes, embedding_layer, device):
            super(Net, self).__init__()

            self.device = device
            self.embedding_layer = embedding_layer
            self.fc1 = nn.Linear(embedding_size * 2, hidden_size) 
            self.relu = nn.ReLU()
            self.fc2 = nn.Linear(hidden_size, hidden_size2) 
            self.relu2 = nn.ReLU()
            self.fc3 = nn.Linear(hidden_size2, num_classes)

        def set_embedding_layer(self, embedding_layer):
            self.embedding_layer = embedding_layer

        def average_sentence(self, sent):
            """ Averages a sentence/multiple sentences by taking the mean of its embeddings

                Args:
                    sent: the given sentence as numbers from the vocab

                Returns:
                    the averaged sentence/sentences as a tensor (size equals the size of one word embedding for each sentence)

            """

            lookup_tensor = torch.tensor(sent, dtype=torch.long).to(self.device)
            embedded_sent = self.embedding_layer(lookup_tensor)

               

            averaged_sent = embedded_sent.mean(dim=0)

            #Reappend the FEE 

            appended_avg = []

            for sentence in averaged_sent:
                inc_FEE = torch.cat((embedded_sent[0][0], sentence),0)
                appended_avg.append(inc_FEE)
                    

            averaged_sent = torch.stack(appended_avg)
                
            return averaged_sent  
                
        def forward(self, x):

            x = Variable(self.average_sentence(x)).to(self.device)

            out = self.fc1(x)
            out = self.relu(out)
            out = self.fc2(out)
            out = self.relu2(out)
            out = self.fc3(out)
            return out   


class Frame_id_network(object):

    def __init__(self, use_cuda, embedding_layer, num_classes):

        #Check for CUDA
        use_cuda = use_cuda and torch.cuda.is_available()
        self.device = torch.device("cuda" if use_cuda else "cpu")    
        print(self.device) 
            
        self.embedding_layer = embedding_layer
        self.num_classes = num_classes

        self.net = Net(embedding_size, hidden_size, hidden_size2, num_classes, embedding_layer, self.device)

        self.net.to(self.device)   

        # Loss and Optimizer
        self.criterion = nn.CrossEntropyLoss()  
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=learning_rate)    


    def train_model(self, train_iter, dataset_size, batch_size):
        """ Trains the model with the given dataset
            
            - uses the model specified in net 

        """
        for epoch in range(num_epochs):   
            #Counter for the iterations
            i = 0

            for batch in iter(train_iter):
                
                sent = batch.Sentence
                sent = torch.tensor(sent, dtype=torch.long)
                
                
                #sent = Variable(average_sentence(sent)).to(self.device)
                labels = Variable(batch.Frame[0]).to(self.device)

                
                # Forward + Backward + Optimize
                self.optimizer.zero_grad()  # zero the gradient buffer
                outputs = self.net(sent)

                loss = self.criterion(outputs,labels)
                loss.backward()
                self.optimizer.step()
                
                if (i+1) % 100 == 0:
                    print ('Epoch [%d/%d], Step [%d/%d], Loss: %.4f' 
                           %(epoch+1, num_epochs, i+1, dataset_size//batch_size, loss.data[0]))

                i += 1

    def predict(self, dataset_iter):
        predictions = []

        for batch in iter(dataset_iter):
            sent = batch.Sentence
            sent = torch.tensor(sent, dtype=torch.long)

            outputs = self.net(sent)
            _, predicted = torch.max(outputs.data, 1)
            predictions.append(predicted.to("cpu"))

        return predictions


    def eval_model(self, dev_iter):
        """ Evaluates the model on the given dataset
            NOTE: only works on gold FEEs, therefore deprecated
                  use f1 evaluation instead
            Args:

            Returns:
                The accuracy reached on the given dataset

        """
        correct = 0.0
        total = 0.0
        for batch in iter(dev_iter):
            sent = batch.Sentence
            sent = torch.tensor(sent, dtype=torch.long)
            labels = Variable(batch.Frame[0]).to(self.device)

            outputs = self.net(sent)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum()
            
        correct = correct.item()

        print(correct)
        print(total)
        accuracy = correct/total

        return accuracy

    def save_model(self, path):
        torch.save(self.net.state_dict(), path)

    def load_model(self, path):
        self.net.load_state_dict(torch.load(path))
