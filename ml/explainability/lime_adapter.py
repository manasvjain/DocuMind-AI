def explain_image_with_lime(predict_fn,image):
    try: from lime import lime_image
    except ImportError as exc: raise RuntimeError("LIME is not installed") from exc
    explainer=lime_image.LimeImageExplainer(random_state=42); explanation=explainer.explain_instance(image,predict_fn,top_labels=3,hide_color=0,num_samples=200)
    return {"top_labels":[int(v) for v in explanation.top_labels],"method":"LIME","num_samples":200}
