import itertools
import pandas as pd

from .nodes import ProteinInteractionNode


def getMetapaths(proteinGraph,start):

	children = getChildren(proteinGraph.graph,start)
	
	if start in proteinGraph.childParentDict.keys(): # if we've got parents, lets remove them from this search
		children = list( set(children) - set(proteinGraph.childParentDict[start]) )  


	proteinMap = {
		True:set(),
		False:set()
	}
	for c in children:
		p = filterNeighbors(proteinGraph.graph,c,True)
		n = filterNeighbors(proteinGraph.graph,c,False)
		posPaths = len(p)
		negPaths = len(n)
			
		for pid in p:
			proteinMap[True].add(pid)
		
	   
		for pid in n:
			proteinMap[False].add(pid)
		   
	return proteinMap

# new graph stuff, things below have been removed 
def filterNeighbors(graph,start,association): # hard coded ... "association"
	return [a for a in graph.adj[start] if "association" in graph.edges[(start,a)].keys() and graph.edges[(start,a)]["association"] == association]

def getChildren(graph,start): # hard coded ... "association"
	return [a for a in graph.adj[start] if "association" not in graph.edges[(start,a)].keys()]


def metapathFeatures(disease,proteinGraph,featureList,idDescription,staticFeatures=None,test=False,loadedLists=None):
	# we compute a genelist.... 
	# get the proteins 
	# for each of the features, compute their metapaths, given an object, and graph+list... then they get joined 
	#print(len(proteinGraph.graph.nodes))
 	
	
	G = proteinGraph.graph # this is our networkx api 
	
	if loadedLists is not None:
		trueP = loadedLists[True] 
		falseP = loadedLists[False]
	else:
		paths = getMetapaths(proteinGraph,disease) #a dictionary with 'True' and 'False' as keys and protein_id as values
		trueP = paths[True]
		falseP = paths[False] 

	print("PREPARING {0} TRUE  ASSOCIATIONS".format(len(trueP)))
	print("PREPARING {0} FALSE ASSOCIATIONS".format(len(falseP)))
	print("")
	print("(NODES IN GRAPH - {0})".format(len(G.nodes)))
	print("(EDGES IN GRAPH - {0})".format(len(G.edges)))

	proteinNodes = [pro for pro in list(G.nodes) if ProteinInteractionNode.isThisNode(pro)] #if isinstance(pro,int)] # or isinstance(pro,np.integer)]
	
	if len(proteinNodes) == 0:
		raise Exception('No protein nodes detected in graph')

	print("(DETECTED PROTEINS - {0})".format(len(proteinNodes)))

	nodeListPairs = []
	for n in featureList:
		nodeListPairs.append((n,[nval for nval in list(G.nodes) if n.isThisNode(nval)]))
	
	metapaths = []
	fh = open('metapath_features.log', 'w') # file to save nodes used for metapaths
	for pair in nodeListPairs:
		nodes = pair[1]
		#print ('PK....', nodes)
		nonTrueAssociations = set(proteinNodes) - trueP
		#print(len(G.nodes),len(nodes),len(trueP),len(nonTrueAssociations))
		METAPATH = pair[0].computeMetapaths(G,nodes,trueP,nonTrueAssociations, idDescription, fh)
		METAPATH = (METAPATH - METAPATH.mean())/METAPATH.std()
		print("SHAPE OF METAPATH FRAME {0} for {1}".format(METAPATH.shape,pair[0]))
		metapaths.append(METAPATH)
	fh.close()

	if test:
		fullList = list(proteinNodes)
		df = pd.DataFrame(fullList, columns=['protein_id'])
		df = df.set_index('protein_id')
	else:
		fullList = list(itertools.product(trueP,[1])) + list(itertools.product(falseP,[0]))
		df = pd.DataFrame(fullList, columns=['protein_id', 'Y'])
		df = df.set_index('protein_id')


	for metapathframe in metapaths:
		# YOU CAN USE THESE TO GET A SUM IF NEED BE
		#print(metapathframe.shape)
		#print(sum(metapathframe.sum(axis=1)))
		
		df = df.join(metapathframe,on="protein_id")
	

	if staticFeatures is not None:
		df = joinStaticFeatures(df,staticFeatures)

	return df



def joinStaticFeatures(dataFrame,featureList):
	
	for feature in featureList:
		# if the file doesn't exist, call it's function.... from an adapter?

		unpickled_df = pd.read_pickle("./"+feature+".csv.pkl")
		# these are needed edits right now for the joins we do, drop the unnamed column and set the index to the protein id
		unpickled_df = unpickled_df.drop(["Unnamed: 0"],axis=1)
		unpickled_df = unpickled_df.set_index('protein_id')

		if feature == "gtex" or feature == "ccle":  # we normed it all except hpa
			unpickled_df = (unpickled_df - unpickled_df.mean())/unpickled_df.std()
		
		dataFrame = dataFrame.join(unpickled_df,on="protein_id")

	return dataFrame
