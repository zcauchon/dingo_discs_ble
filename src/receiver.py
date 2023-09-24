import argparse
import logging
import sys
from typing import Iterable, Tuple

from pyflink.common import WatermarkStrategy, Types
from pyflink.common.typeinfo import RowTypeInfo
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode, ProcessWindowFunction
from pyflink.datastream.window import SlidingEventTimeWindows, Time
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer, DeserializationSchema
from pyflink.datastream.formats.json import JsonRowDeserializationSchema

class WindowCounter(ProcessWindowFunction):

    def process(self, key: str, context: ProcessWindowFunction.Context,
                elements: Iterable[Tuple[str, int]]) -> Iterable[str]:
        count = 0
        for _ in elements:
            count += 1
        yield "Window: {} count: {} Key {}".format(context.window(), count, key)

def check_for_throw():
    # Watches the entire stream and look at 3 sec windows to identify throws
    # If throw is found capture window and send to db sink
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    env.set_parallelism(1)

    row_type_info = Types.ROW_NAMED(
        ['device', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'rx', 'ry', 'rz'],
        [Types.STRING(), Types.BIG_DEC(), Types.BIG_DEC(), Types.BIG_DEC(), Types.BIG_DEC(), Types.BIG_DEC(), Types.BIG_DEC(), Types.BIG_DEC(), Types.BIG_DEC(), Types.BIG_DEC()])
    deserialization_schema = JsonRowDeserializationSchema.Builder().type_info(row_type_info).build()

    kafkaSource = KafkaSource.builder() \
        .set_bootstrap_servers('127.0.0.1:9092') \
        .set_topics("disc_events") \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(deserialization_schema) \
        .build()
    
    ds = env.from_source(kafkaSource, WatermarkStrategy.for_monotonous_timestamps(), "disc_events_source")

    results = ds \
        .key_by(lambda x: x[0]) \
        .window(SlidingEventTimeWindows.of(Time.seconds(3), Time.seconds(2))) \
        .process(WindowCounter())

    results.print()

    env.execute()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    check_for_throw()