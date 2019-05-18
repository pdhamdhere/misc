#include <iostream>

/*
 * In disjointed DAG representing courses and pre-requisites, identify all nodes
 * with 0 in-degree and for each such node, generate all possible paths that 
 * originate from the node.
 * For e.g.
 *          0   6
 *         / \ /               
 *        1   2   4     
 *       / \ /
 *      3   5
 * 
 * Input:
 * 7 
 * 0, 1
 * 0, 2
 * 1, 3
 * 1, 5
 * 2, 5
 * 6, 2
 * 
 * Expected Output (any order):
 * 0->1->3
 * 0->1->5 
 * 0->2->5
 * 4
 * 6->2->5
 * 
 */

struct Graph
{
   int numVertices;
   struct node **adjList;
   int *indegree;
};

// Node in adjacency list
struct node
{
   int vertex;
   struct node *next;
};

// Create & initialize graph structure
struct Graph *createGraph(int numVertices)
{
   struct Graph *graph = (struct Graph *)malloc(sizeof(struct Graph));
   graph->numVertices = numVertices;
   graph->adjList = (struct node **)malloc(sizeof(struct node) * numVertices);
   graph->indegree = (int *)malloc(sizeof(int) * numVertices);

   for (int i = 0; i < numVertices; i++)
   {
      graph->adjList[i] = NULL;
      graph->indegree[i] = 0;
   }
   return graph;
}

// Adds edges to Graph and calculate in-degree as edges are added
void getEdges(struct Graph *graph)
{
   int src, dest;
   while (scanf("%d, %d", &src, &dest) != EOF)
   {
      struct node *newNode = (struct node *)malloc(sizeof(struct node));
      newNode->vertex = dest;
      newNode->next = graph->adjList[src];
      graph->adjList[src] = newNode;
      graph->indegree[dest] = graph->indegree[dest] + 1;
   }
}

void print(struct Graph *graph)
{
   for (int i = 0; i < graph->numVertices; i++)
   {
      struct node *tmp = graph->adjList[i];
      printf("Vertex %d , Indegree: %d Edges: \n", i, graph->indegree[i]);
      while (tmp)
      {
         printf("%d -> %d\n", i, tmp->vertex);
         tmp = tmp->next;
      }
   }
}

void printPath(int path[], int index)
{
   for (int i = 0; i < index; i++)
   {
      if (i == (index - 1)) // Make hackerRank happy!
         printf("%d", path[i]);
      else
         printf("%d->", path[i]);
   }
   printf("\n");
}

void DFS(struct Graph *graph, int start, int path[], int index)
{
   struct node *tmp = graph->adjList[start];

   path[index] = start;
   index++;

   // Check if leaf and print path
   if (graph->adjList[start] == NULL)
   {
      printPath(path, index);
   }
   while (tmp)
   {
      int dest = tmp->vertex;
      DFS(graph, dest, path, index);
      tmp = tmp->next;
   }
   index--;
}

int main()
{
   /* Enter your code here. Read input from STDIN. Print output to STDOUT */
   int numVertices;
   struct Graph *graph;
   scanf("%d", &numVertices);
   graph = createGraph(numVertices);
   getEdges(graph);
   //print(graph);

   int *path = (int *)malloc(sizeof(int) * numVertices);
   int index = 0;

   // DFS for each vertex with 0 in-degree
   for (int i = 0; i < graph->numVertices; i++)
   {
      if (graph->indegree[i] == 0)
      {
         DFS(graph, i, path, index);
      }
   }

   return 0;
}