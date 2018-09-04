import argparse
import ast
import pprint

import mxnet as mx
from mxnet.module import Module

from symdata.bbox import im_detect
from symdata.loader import load_test, generate_batch
from symdata.vis import vis_detection
from symnet.model import load_param, check_shape


def load_CNN(srcargs):
    ctx = mx.cpu(0)
    arg_params, aux_params = load_param(srcargs.params, ctx=ctx)
    cnnargs = cnnparse_args()
    cnnargs.src = srcargs.src
    cnnargs.logic = srcargs.logic
    print("success parser args")
    sym = get_network(cnnargs.network, cnnargs)
    data_names = ['data', 'im_info']
    label_names = None
    mod = Module(sym, data_names, label_names, context=ctx)
    return mod,cnnargs,arg_params,aux_params

def Run(mod, cnnargs, arg_params, aux_params,boxid=0):
    class_names = get_class_names(cnnargs.dataset, cnnargs)
    # print config
    #print('called with cnnargs\n{}'.format(pprint.pformat(vars(cnnargs))))

    # setup context
    #if args.gpu:
    #    ctx = mx.gpu(int(args.gpu))
    #else:
    #    ctx = mx.cpu(0)

    # load single test
    im_tensor, im_info, im_orig = load_test(cnnargs.image, short=cnnargs.img_short_side, max_size=cnnargs.img_long_side,
                                            mean=cnnargs.img_pixel_means, std=cnnargs.img_pixel_stds)

    # generate data batch
    data_batch = generate_batch(im_tensor, im_info)

    # load params
    #arg_params, aux_params = load_param(args.params, ctx=ctx)

    # produce shape max possible
    #data_names = ['data', 'im_info']
    #label_names = None
    data_shapes = [('data', (1, 3, cnnargs.img_long_side, cnnargs.img_long_side)), ('im_info', (1, 3))]
    label_shapes = None

    # check shapes
    #check_shape(sym, data_shapes, arg_params, aux_params)

    # create and bind module
    #mod = Module(sym, data_names, label_names, context=ctx)
    mod.bind(data_shapes, label_shapes, for_training=False)
    mod.init_params(arg_params=arg_params, aux_params=aux_params)

    # forward
    mod.forward(data_batch)
    rois, scores, bbox_deltas = mod.get_outputs()
    rois = rois[:, 1:]
    scores = scores[0]
    bbox_deltas = bbox_deltas[0]
    im_info = im_info[0]

    # decode detection
    det = im_detect(rois, scores, bbox_deltas, im_info,
                    bbox_stds=cnnargs.rcnn_bbox_stds, nms_thresh=cnnargs.rcnn_nms_thresh,
                    conf_thresh=cnnargs.rcnn_conf_thresh)

    # print out
    cnnResult = []
    out = open(cnnargs.out,'w')
    box_id = 0
    print("in model.py run: boxid = ",boxid)
    if boxid != 0:
        for [cls, conf, x1, y1, x2, y2] in det:
            if cls > 0 and conf > cnnargs.vis_thresh:
                print(class_names[int(cls)], conf, x1, y1, x2, y2, boxid, sep=' ', file=out)
                cnnResult.append([class_names[int(cls)], conf, x1, y1, x2, y2, boxid])
    else:    
        for [cls, conf, x1, y1, x2, y2] in det:
            if cls > 0 and conf > cnnargs.vis_thresh:
                print(class_names[int(cls)], conf, x1, y1, x2, y2, box_id, sep=' ', file=out)
                cnnResult.append([class_names[int(cls)], conf, x1, y1, x2, y2, box_id])
                box_id += 1
    out.close()

    # if vis
    if cnnargs.vis:
        vis_detection(im_orig, det, class_names, thresh=cnnargs.vis_thresh)
    return cnnResult    


def cnnparse_args():
    cnnparser = argparse.ArgumentParser(description='Demonstrate a Faster R-CNN network',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cnnparser.add_argument('--network', type=str, default='resnet101', help='base network')
    cnnparser.add_argument('--params', type=str, default='rcnn/resnet_voc0712-0010.params', help='path to trained model')
    cnnparser.add_argument('--dataset', type=str, default='voc', help='training dataset')
    cnnparser.add_argument('--src', type=str, help='src video')
    cnnparser.add_argument('--logic', type=str, help='logic')
    cnnparser.add_argument('--image', type=str, default='', help='path to test image')
    cnnparser.add_argument('--gpu', type=str, default='0', help='gpu device eg. 0')
    cnnparser.add_argument('--vis', action='store_true', help='display results')
    cnnparser.add_argument('--out', type=str, help='output')
    cnnparser.add_argument('--vis-thresh', type=float, default=0.3, help='threshold display boxes')
    # faster rcnn params
    cnnparser.add_argument('--img-short-side', type=int, default=600)
    cnnparser.add_argument('--img-long-side', type=int, default=1000)
    cnnparser.add_argument('--img-pixel-means', type=str, default='(0.0, 0.0, 0.0)')
    cnnparser.add_argument('--img-pixel-stds', type=str, default='(1.0, 1.0, 1.0)')
    cnnparser.add_argument('--rpn-feat-stride', type=int, default=16)
    cnnparser.add_argument('--rpn-anchor-scales', type=str, default='(8, 16, 32)')
    cnnparser.add_argument('--rpn-anchor-ratios', type=str, default='(0.5, 1, 2)')
    cnnparser.add_argument('--rpn-pre-nms-topk', type=int, default=6000)
    cnnparser.add_argument('--rpn-post-nms-topk', type=int, default=300)
    cnnparser.add_argument('--rpn-nms-thresh', type=float, default=0.7)
    cnnparser.add_argument('--rpn-min-size', type=int, default=16)
    cnnparser.add_argument('--rcnn-num-classes', type=int, default=21)
    cnnparser.add_argument('--rcnn-feat-stride', type=int, default=16)
    cnnparser.add_argument('--rcnn-pooled-size', type=str, default='(14, 14)')
    cnnparser.add_argument('--rcnn-batch-size', type=int, default=1)
    cnnparser.add_argument('--rcnn-bbox-stds', type=str, default='(0.1, 0.1, 0.2, 0.2)')
    cnnparser.add_argument('--rcnn-nms-thresh', type=float, default=0.3)
    cnnparser.add_argument('--rcnn-conf-thresh', type=float, default=1e-3)
    cnnargs = cnnparser.parse_args()
    cnnargs.img_pixel_means = ast.literal_eval(cnnargs.img_pixel_means)
    cnnargs.img_pixel_stds = ast.literal_eval(cnnargs.img_pixel_stds)
    cnnargs.rpn_anchor_scales = ast.literal_eval(cnnargs.rpn_anchor_scales)
    cnnargs.rpn_anchor_ratios = ast.literal_eval(cnnargs.rpn_anchor_ratios)
    cnnargs.rcnn_pooled_size = ast.literal_eval(cnnargs.rcnn_pooled_size)
    cnnargs.rcnn_bbox_stds = ast.literal_eval(cnnargs.rcnn_bbox_stds)
    return cnnargs


def get_voc_names(args):
    from symimdb.pascal_voc import PascalVOC
    args.rcnn_num_classes = len(PascalVOC.classes)
    return PascalVOC.classes


def get_coco_names(args):
    from symimdb.coco import coco
    args.rcnn_num_classes = len(coco.classes)
    return coco.classes


def get_vgg16_test(args):
    from symnet.symbol_vgg import get_vgg_test
    if not args.params:
        args.params = 'model/vgg16-0010.params'
    args.img_pixel_means = (123.68, 116.779, 103.939)
    args.img_pixel_stds = (1.0, 1.0, 1.0)
    args.net_fixed_params = ['conv1', 'conv2']
    args.rpn_feat_stride = 16
    args.rcnn_feat_stride = 16
    args.rcnn_pooled_size = (7, 7)
    return get_vgg_test(anchor_scales=args.rpn_anchor_scales, anchor_ratios=args.rpn_anchor_ratios,
                        rpn_feature_stride=args.rpn_feat_stride, rpn_pre_topk=args.rpn_pre_nms_topk,
                        rpn_post_topk=args.rpn_post_nms_topk, rpn_nms_thresh=args.rpn_nms_thresh,
                        rpn_min_size=args.rpn_min_size,
                        num_classes=args.rcnn_num_classes, rcnn_feature_stride=args.rcnn_feat_stride,
                        rcnn_pooled_size=args.rcnn_pooled_size, rcnn_batch_size=args.rcnn_batch_size)

def get_resnet50_test(args):
    from symnet.symbol_resnet import get_resnet_test
    if not args.params:
        args.params = 'model/resnet50-0010.params'
    args.img_pixel_means = (0.0, 0.0, 0.0)
    args.img_pixel_stds = (1.0, 1.0, 1.0)
    args.rpn_feat_stride = 16
    args.rcnn_feat_stride = 16
    args.rcnn_pooled_size = (14, 14)
    return get_resnet_test(anchor_scales=args.rpn_anchor_scales, anchor_ratios=args.rpn_anchor_ratios,
                           rpn_feature_stride=args.rpn_feat_stride, rpn_pre_topk=args.rpn_pre_nms_topk,
                           rpn_post_topk=args.rpn_post_nms_topk, rpn_nms_thresh=args.rpn_nms_thresh,
                           rpn_min_size=args.rpn_min_size,
                           num_classes=args.rcnn_num_classes, rcnn_feature_stride=args.rcnn_feat_stride,
                           rcnn_pooled_size=args.rcnn_pooled_size, rcnn_batch_size=args.rcnn_batch_size,
                           units=(3, 4, 6, 3), filter_list=(256, 512, 1024, 2048))


def get_resnet101_test(args):
    from symnet.symbol_resnet import get_resnet_test
    if not args.params:
        args.params = 'model/resnet101-0010.params'
    args.img_pixel_means = (0.0, 0.0, 0.0)
    args.img_pixel_stds = (1.0, 1.0, 1.0)
    args.rpn_feat_stride = 16
    args.rcnn_feat_stride = 16
    args.rcnn_pooled_size = (14, 14)
    return get_resnet_test(anchor_scales=args.rpn_anchor_scales, anchor_ratios=args.rpn_anchor_ratios,
                           rpn_feature_stride=args.rpn_feat_stride, rpn_pre_topk=args.rpn_pre_nms_topk,
                           rpn_post_topk=args.rpn_post_nms_topk, rpn_nms_thresh=args.rpn_nms_thresh,
                           rpn_min_size=args.rpn_min_size,
                           num_classes=args.rcnn_num_classes, rcnn_feature_stride=args.rcnn_feat_stride,
                           rcnn_pooled_size=args.rcnn_pooled_size, rcnn_batch_size=args.rcnn_batch_size,
                           units=(3, 4, 23, 3), filter_list=(256, 512, 1024, 2048))

def get_class_names(dataset, args):
    datasets = {
        'voc': get_voc_names,
        'coco': get_coco_names
    }
    if dataset not in datasets:
        raise ValueError("dataset {} not supported".format(dataset))
    return datasets[dataset](args)


def get_network(network, args):
    networks = {
        'vgg16': get_vgg16_test,
        'resnet50': get_resnet50_test,
        'resnet101': get_resnet101_test
    }
    if network not in networks:
        raise ValueError("network {} not supported".format(network))
    return networks[network](args)
