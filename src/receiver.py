import logging
import sys

from pyflink.common import WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.window import SlidingEventTimeWindows, Time
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer, KafkaOffsetResetStrategy

from models.disc_event import DiscEvent
from entities.throw_detector import ThrowDetector

def check_for_throw():
    # Watches the entire stream and look at 3 sec windows to identify throws
    # If throw is found capture window and send to db sink
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    env.set_parallelism(1)
    
    disc_source = KafkaSource.builder() \
        .set_bootstrap_servers('127.0.0.1:9092') \
        .set_topics("disc_events") \
        .set_group_id('disc_group') \
        .set_starting_offsets(KafkaOffsetsInitializer.committed_offsets(offset_reset_strategy=KafkaOffsetResetStrategy.LATEST)) \
        .set_value_only_deserializer(DiscEvent.getFlinkDeserializer()) \
        .build()

    ds = env.from_source(disc_source, WatermarkStrategy.for_monotonous_timestamps(), "disc_events_source")

    throws = ds \
        .key_by(lambda x: x[0]) \
        .window(SlidingEventTimeWindows.of(Time.seconds(4), Time.seconds(2))) \
        .process(ThrowDetector())

    throws.print()

    env.execute()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    check_for_throw()