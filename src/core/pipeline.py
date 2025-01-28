from collections import deque

class Pipeline:

    def __init__(self, name: str, input_keys: list[str], output_keys: list[str], process: callable[dict, dict, dict]):
        """
        Initialize a new pipeline instance.
        Args:
            name (str): The name of the pipeline.
            input_keys (list[str]): A list of keys for the input data.
            output_keys (list[str]): A list of keys for the output data.
            process (callable): A callable that processes the data. It should accept three dictionaries as arguments and return a dictionary.
        """

        self.name = name
        self.input_keys = input_keys
        self.output_keys = output_keys
        self.process = process

    def process(self, inputs: dict, **kwargs) -> dict:
        """
        Processes the given inputs and returns the result.
        Args:
            inputs (dict): A dictionary of input data to be processed.
            **kwargs: Additional keyword arguments.
        Returns:
            dict: A dictionary containing the processed results.
        """

        return self.process(inputs, **kwargs)

    def get_input_keys(self):
        """
        Retrieve the input keys for the pipeline.
        Returns:
            list: A list of input keys.
        """
        
        return self.input_keys

    def get_output_keys(self):
        """
        Retrieve the output keys of the pipeline.
        Returns:
            list: A list of output keys.
        """

        return self.output_keys

class PipelineOrchestrator:

    def __init__(self):
        self.pipelines = []

    def register(self, pipeline: Pipeline):
        """
        Registers a new pipeline if it is valid.
        Args:
            pipeline (Pipeline): The pipeline to be registered.
        Returns:
            None
        """

        if self._check_pipeline_validity(pipeline):
            self.pipelines.append(pipeline)
    
    def process(self, name: str, inputs: dict, **kwargs) -> dict:
        """
        Processes the given inputs using the specified pipeline.
        Args:
            name (str): The name of the pipeline to be used.
            inputs (dict): A dictionary of input data to be processed.
            **kwargs: Additional keyword arguments.
        Returns:
            dict: A dictionary containing the processed results.
        """

        chain = self._generate_chain(name)
        result = inputs
        for p in chain:
            result = p.process(result, **kwargs)
        return result

    def _find_pipeline(self, name: str) -> Pipeline:
        for p in self.pipelines:
            if p.name == name:
                return p
        return None

    def _check_pipeline_validity(self, pipeline: Pipeline) -> bool:
        for p in self.pipelines:
            if p.name == pipeline.name:
                raise ValueError(f"Pipeline with name '{pipeline.name}' already exists.")
            
        # multiple same output keys causes dependency issues
        for key in pipeline.output_keys:
            if key in pipeline.output_keys:
                raise ValueError(f"Output key '{key}' already exists in another pipeline.")
        
        # use DFS searching for dependency loop
        stack = []
        visited = set()
        for p in self.pipelines:
            if p.name not in visited and self._check_pipeline_loop(stack, visited, p):
                raise ValueError(f"Pipeline '{p.name}' has a dependency loop.")

        return True

    def _check_pipeline_loop(self, stack: list[str], visited: set[str], pipeline: Pipeline) -> bool:
        stack.append(pipeline.name)
        visited.add(pipeline.name)
        for key in pipeline.output_keys:
            for p in self.pipelines:
                if key in p.input_keys:
                    if p.name in visited:
                        return True
                    if self._check_pipeline_loop(stack, visited, p):
                        return True
        stack.pop()
        return False

    def _generate_chain(self, name: str) -> list[Pipeline]:
        chain = []
        p = self._find_pipeline(name)
        dq = deque([p])
        visited = set([p.name])
        if p is None:
            raise ValueError(f"Pipeline '{name}' does not exist.")
        while dq:
            p = dq.popleft()
            chain.append(p)
            for key in p.input_keys:
                for dep in self.pipelines:
                    if key in dep.output_keys and dep.name not in visited:
                        dq.append(dep)
                        visited.add(dep.name)
        return reversed(chain)
