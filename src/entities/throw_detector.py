from typing import Iterable, Tuple
import itertools

from pyflink.common.typeinfo import Types
from pyflink.datastream import ProcessWindowFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor

class ThrowDetector(ProcessWindowFunction):

    thres_ax = 10

    def __init__(self) -> None:
        pass

    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor(
            "previous_ax",  # the state name
            Types.BIG_DEC()  # type information
        )
        self.previous_ax = runtime_context.get_state(descriptor)

    def process(self, key: str, context: ProcessWindowFunction.Context,
                elements: Iterable[Tuple[str, float, float, float, float, float, float, float, float, float]]) -> Iterable[str]:
        
        print('\nWindow', context.window())
        for el in itertools.islice(elements, (int(len(elements)/4))):
            previous_ax = self.previous_ax.value()
            if previous_ax is None:
                previous_ax = 0
            if el[1] - previous_ax > self.thres_ax:
                print(f'Thow idenified! {previous_ax} -> {el[1]}')
                # updat this to build new DiscThrow(elements)
                self.previous_ax.clear()
                yield elements
                break
            self.previous_ax.update(el[1])