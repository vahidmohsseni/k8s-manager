from pathlib import Path
from utils import UPLOAD_DIR, get_model_path
from utils import logger
from time import time, sleep
from config import TRAINED_MODEL_SUFFIX

QUEUE = []


def train():
    """Training process that should run parallel to the server"""
    logger.info("Trainer process created")
    while True:
        if QUEUE:
            train_model(QUEUE[0])
            model = QUEUE.pop(0)
            logger.info(f"Finished training model {model}")


def enqueue_model(model_id: str):
    QUEUE.append(model_id)


def model_in_training(model_id: str):
    return model_id + TRAINED_MODEL_SUFFIX in QUEUE


def train_model(model_id: str):
    """Train the model. Returns the filename of the trained model."""
    logger.info(f"Beginning training for model {model_id}")
    sleep(20)
    new_model = mock_train_model(model_id)
    validate_model(new_model.name)


def validate_model(model_id: str) -> bool:
    """Validate model integrity."""
    logger.info(f"Validating model {model_id}")
    return True


def mock_train_model(model_id: str) -> Path:
    """Mock function that actually just creates a renamed copy of the file."""
    source = get_model_path(model_id)
    if not source:
        raise FileNotFoundError("File does not exist locally.")
    start = time()
    parts = source.name.split(".")
    parts = [parts[0], TRAINED_MODEL_SUFFIX, ".", parts[1]]
    destination = Path(UPLOAD_DIR, "".join(parts))
    with open(source, "rb") as source_file, open(destination, "wb") as dest_file:
        while True:
            block = source_file.read(1024 * 1024 * 16)
            if not block:
                break
            dest_file.write(block)
    logger.info("Training took {:.2f} seconds.".format(time() - start))
    return destination
