# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 20:51:40 2018

@author: admin
"""
import numpy as np
import sys
import tensorflow as tf
from PIL import Image
np.set_printoptions(threshold=np.inf)

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("/home/bowen/models/research")
from object_detection.utils import ops as utils_ops


def Load_RCNN(args):
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(args.modelpath, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    with detection_graph.as_default():
        sess = tf.Session()
    return detection_graph, sess


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

def run_inference_for_single_image(image, graph, sess):
    with graph.as_default():
        # Get handles to input and output tensors
        ops = tf.get_default_graph().get_operations()
        all_tensor_names = {output.name for op in ops for output in op.outputs}
        tensor_dict = {}
        for key in [
                'num_detections', 'detection_boxes', 'detection_scores',
                'detection_classes', 'detection_masks'
            ]:
            tensor_name = key + ':0'
            if tensor_name in all_tensor_names:
                tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)
        if 'detection_masks' in tensor_dict:
        # The following processing is only for single image
            detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
            detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
            # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
            real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
            detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
            detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
            detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(detection_masks, detection_boxes, image.shape[0], image.shape[1])
            detection_masks_reframed = tf.cast(tf.greater(detection_masks_reframed, 0.5), tf.uint8)
            # Follow the convention by adding back the batch dimension
            tensor_dict['detection_masks'] = tf.expand_dims(detection_masks_reframed, 0)
        image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

        # Run inference
        output_dict = sess.run(tensor_dict,
                         feed_dict={image_tensor: np.expand_dims(image, 0)})

        # all outputs are float32 numpy arrays, so convert types as appropriate
        output_dict['num_detections'] = int(output_dict['num_detections'][0])
        output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
        output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
        output_dict['detection_scores'] = output_dict['detection_scores'][0]
        if 'detection_masks' in output_dict:
            output_dict['detection_masks'] = output_dict['detection_masks'][0]
    return output_dict


def Run(image_path,detection_graph,session,boxid):
    image = Image.open(image_path)
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)
    # Actual detection.
    output_dict = run_inference_for_single_image(image_np, detection_graph, session)
    remove_index = []
    for i in range(len(output_dict['detection_classes'])):
        if output_dict['detection_classes'][i] != 3:
           remove_index.append(i)
    for i in range(len(output_dict['detection_scores'])):
        if output_dict['detection_scores'][i] <= 0.3:
           remove_index.append(i)
    new_output = {}
    new_output['detection_classes'] = []
    new_output['detection_scores'] = []
    new_output['detection_boxes'] = []
    new_output['bbox_id'] = []
    count = 0
    for i in range(len(output_dict['detection_boxes'])):
        if i in remove_index:
           continue
        else:
           new_output['detection_classes'].append(output_dict['detection_classes'][i])
           new_output['detection_scores'].append(output_dict['detection_scores'][i])
           new_output['detection_boxes'].append(output_dict['detection_boxes'][i])
           if boxid == -1:
               new_output['bbox_id'].append(count)
               count += 1
           else:
               new_output['bbox_id'].append(boxid)
    
    print(new_output['detection_boxes'])
    return new_output
