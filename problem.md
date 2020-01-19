From https://app.trinethire.com/companies/22646-shoreline-software-inc/jobs/16711-software-engineer-distributed-systems

If interested, please design and implement a solution to the following problem.  Please use source control for your solution and include a link to the repository. If you do not want to apply using this web system, please email the solution (attach or include link to repo/gist) and a resume to jobs@shorelinesoftware.com. Please include "Software Engineer - Distributed Systems" in the subject of your email.

Below, you will find types and interfaces specified in Elixir, Shoreline's main programming language. However, we ask that you please complete your solution in the language of your choice.

### Problem

Imagine you are building a system to assign unique numbers to each resource that you manage. You want the ids to be guaranteed unique i.e. no UUIDs. Since these ids are globally unique, each id can only be given out at most once. The ids are 64 bits long.

Your service is composed of a set of nodes, each running one process serving ids. A caller will connect to one of the nodes and ask it for a globally unique id. There are a fixed number of nodes in the system, up to 1024. Each node has a numeric id, 0 <= id <= 1023. Each node knows its id at startup and that id never changes for the node.

Your task is to implement get_id. When a caller requests a new id, the node it connects to calls its internal get_id function to get a new, globally unique id.

```elixir
defmodule GlobalId do
  @moduledoc """
  GlobalId module contains an implementation of a guaranteed globally unique id system.
  """

  @doc """
  Please implement the following function.
  64 bit non negative integer output
  """
  @spec get_id(???) :: non_neg_integer
  def get_id(???) do

  end

  #
  # You are given the following helper functions
  # Presume they are implemented - there is no need to implement them.
  #

  @doc """
  Returns your node id as an integer.
  It will be greater than or equal to 0 and less than or equal to 1024.
  It is guaranteed to be globally unique.
  """
  @spec node_id() :: non_neg_integer
  def node_id

  @doc """
  Returns timestamp since the epoch in milliseconds.
  """
  @spec timestamp() :: non_neg_integer
  def timestamp
end
```

You may add other functions to the implementation in order to complete your solution.

Please determine the interface to get_id and please provide an explanation as to what parameters it takes in comments.

Assume that any node will not receive more than 100,000 requests per second.

Please write answers to the following discussion questions and include them in your solution as comments:

1. Please describe your solution to get_id and why it is correct i.e. guaranteed globally unique.
1. Please explain how your solution achieves the desired performance i.e. 100,000 or more requests per second per node. How did you verify this?
1. Please enumerate possible failure cases and describe how your solution correctly handles each case. How did you verify correctness? Some example cases:

How do you manage uniqueness after a node crashes and restarts?

How do you manage uniqueness after the entire system fails and restarts?

How do you handle software defects?

We will evaluate your solution for correctness, simplicity, clarity, and robustness. Solutions with minimal coordination and persistent storage are best. Solutions that provide benchmarks for performance and tests to verify correctness are best.

If you have any clarifying questions, please email: jobs@shorelinesoftware.com
