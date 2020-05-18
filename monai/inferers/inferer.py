# Copyright 2020 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABC, abstractmethod
from .utils import sliding_window_inference


class Inferer(ABC):
    """Inferer is the base class of all kinds of inferers, which execute inference on model.
    It can support complicated operations during inference, like SlidingWindow.

    """
    @abstractmethod
    def __call__(self, inputs, network):
        """Unified callable function API of Inferers.

        Args:
            inputs (torch.tensor): model input data for inference.
            network (Network): target model to execute inference.

        """
        raise NotImplementedError('subclass will implement the operations.')


class RegularInferer(Inferer):
    """SimpleInferer is the normal inference method that run model forward() directly.

    """
    def __init__(self):
        Inferer.__init__(self)

    def __call__(self, inputs, network):
        """Unified callable function API of Inferers.

        Args:
            inputs (torch.tensor): model input data for inference.
            network (Network): target model to execute inference.

        """
        return network(inputs)


class SlidingWindowInferer(Inferer):
    """Use SlidingWindow method to execute inference, run windows on model based on sw_batch_size.

    Args:
        roi_size (list, tuple): the window size to execute SlidingWindow evaluation.
        sw_batch_size (int): the batch size to run window slices.
        overlap (float): Amount of overlap between scans.
        blend_mode (str): How to blend output of overlapping windows. Options are 'constant', 'guassian'. 'constant'
            gives equal weight to all predictions while gaussian gives less weight to predictions on edges of windows.

    Note:
        the "sw_batch_size" here is to run a batch of window slices of 1 input image,
        not batch size of input images.

    """
    def __init__(self, roi_size, sw_batch_size=1, overlap=0.25, blend_mode="constant"):
        Inferer.__init__(self)
        assert isinstance(roi_size, (list, tuple)), 'must specify the roi size for SlidingWindow.'
        self.roi_size = roi_size
        self.sw_batch_size = sw_batch_size
        self.overlap = overlap
        self.blend_mode = blend_mode

    def __call__(self, inputs, network):
        """Unified callable function API of Inferers.

        Args:
            inputs (torch.tensor): model input data for inference.
            network (Network): target model to execute inference.

        """
        return sliding_window_inference(inputs, self.roi_size, self.sw_batch_size, network,
                                        self.overlap, self.blend_mode)
