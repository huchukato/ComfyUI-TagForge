from .py import endpoints, wildcard_processor


NODE_CLASS_MAPPINGS = {
    "WildcardProcessor": wildcard_processor.WildcardProcessorNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "WildcardProcessor": "🃏 Wildcard Processor",
}
WEB_DIRECTORY = "./web"

