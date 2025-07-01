"""
Mock response data for API endpoints to avoid expensive AI calls during testing.
"""

from typing import Dict, Any, List, Union


def get_mock_toc_response(book_idea: str = "") -> List[Dict[str, Any]]:
    """Mock TOC response - structured JSON matching Section model."""
    return [
        {
            "section_name": "Introduction: The Dawn of AI-Powered Health",
            "section_ideas": [
                "The revolutionary potential of artificial intelligence in healthcare",
                "Current limitations of traditional health monitoring",
                "Vision for personalized, predictive healthcare",
                "Overview of retinal imaging technology",
                "The eye as a window to systemic health",
                "AI's ability to detect patterns invisible to human observers",
                "Democratizing advanced medical diagnostics",
                "Privacy and ethical considerations in AI health",
                "The future of preventive medicine",
                "Setting expectations for this book's journey"
            ]
        },
        {
            "section_name": "The Science Behind Retinal Health Assessment",
            "section_ideas": [
                "Anatomy of the retina and its vascular system",
                "How systemic diseases manifest in retinal changes",
                "Diabetes and diabetic retinopathy indicators",
                "Hypertension effects on retinal blood vessels",
                "Early signs of cardiovascular disease in the eye",
                "Neurological conditions visible through retinal analysis",
                "Age-related changes vs pathological changes",
                "The relationship between retinal and brain health",
                "Inflammation markers visible in retinal imaging",
                "Genetic factors influencing retinal health"
            ]
        },
        {
            "section_name": "AI Technology Foundations",
            "section_ideas": [
                "Machine learning fundamentals for medical imaging",
                "Deep learning architectures for image analysis",
                "Training datasets and medical image quality",
                "Computer vision techniques for retinal scanning",
                "Pattern recognition in vascular structures",
                "Feature extraction from retinal photographs",
                "Validation methodologies for AI medical tools",
                "Accuracy metrics and clinical relevance",
                "Handling edge cases and ambiguous results",
                "Continuous learning and model improvement"
            ]
        },
        {
            "section_name": "Current Applications and Case Studies",
            "section_ideas": [
                "Real-world deployment examples",
                "Clinical trial results and outcomes",
                "Comparison with traditional screening methods",
                "Cost-effectiveness analysis",
                "Patient acceptance and user experience",
                "Healthcare provider adoption challenges",
                "Integration with existing medical workflows",
                "Regulatory approval processes",
                "International implementation variations",
                "Success stories from pilot programs"
            ]
        },
        {
            "section_name": "The Personal Health Revolution",
            "section_ideas": [
                "Shift from reactive to proactive healthcare",
                "Consumer-grade vs medical-grade devices",
                "Smartphone-based retinal imaging possibilities",
                "Home monitoring and telemedicine integration",
                "Wearable technology convergence",
                "Personal health data ownership",
                "Building individual health baselines",
                "Longitudinal health tracking benefits",
                "Empowering patients with their own data",
                "The quantified self movement in healthcare"
            ]
        },
        {
            "section_name": "Implementation Challenges and Solutions",
            "section_ideas": [
                "Technical barriers to widespread adoption",
                "Healthcare system integration complexities",
                "Regulatory compliance requirements",
                "Training healthcare professionals",
                "Patient privacy and data security",
                "Cost barriers and insurance coverage",
                "Quality control and standardization",
                "Cross-platform compatibility issues",
                "Rural and underserved population access",
                "Scaling challenges for global deployment"
            ]
        },
        {
            "section_name": "Future Horizons and Emerging Technologies",
            "section_ideas": [
                "Next-generation AI algorithms and capabilities",
                "Multi-modal health assessment integration",
                "Real-time health monitoring possibilities",
                "Predictive modeling for disease prevention",
                "Personalized treatment recommendations",
                "Integration with genomic data",
                "Augmented reality in medical diagnostics",
                "Edge computing for instant analysis",
                "Blockchain for secure health data sharing",
                "The convergence of AI, IoT, and healthcare"
            ]
        },
        {
            "section_name": "Ethical Considerations and Best Practices",
            "section_ideas": [
                "Informed consent in AI-driven healthcare",
                "Algorithmic bias and fairness issues",
                "Transparency in AI decision-making",
                "Patient autonomy and choice",
                "Healthcare provider liability questions",
                "Data governance and stewardship",
                "Cross-cultural considerations",
                "Equity in healthcare access",
                "Professional ethics for AI developers",
                "Building trust between patients and AI systems"
            ]
        },
        {
            "section_name": "Building Your Own AI Health Monitoring System",
            "section_ideas": [
                "Selecting appropriate hardware and software",
                "Understanding device specifications and limitations",
                "Setting up your personal health dashboard",
                "Interpreting AI-generated health insights",
                "When to seek professional medical advice",
                "Creating a personal health monitoring routine",
                "Data backup and long-term storage strategies",
                "Sharing data with healthcare providers",
                "Troubleshooting common issues",
                "Staying updated with technology advances"
            ]
        },
        {
            "section_name": "Conclusion: Your Health, Your Future",
            "section_ideas": [
                "Recap of key insights and technologies",
                "The transformation of healthcare delivery",
                "Individual empowerment through technology",
                "The importance of early detection and prevention",
                "Building a sustainable health monitoring practice",
                "Contributing to the global health data ecosystem",
                "Advocating for AI transparency and ethics",
                "Preparing for the next wave of health innovations",
                "Taking action on your health journey",
                "Final thoughts on the democratization of healthcare"
            ]
        }
    ]


def get_mock_draft_response() -> Dict[str, str]:
    """Mock draft response - full book markdown."""
    return {
        "markdown": """## Introduction: The Dawn of AI-Powered Health

The revolution in healthcare is happening now, and it's powered by artificial intelligence. In this opening chapter, we explore how AI is transforming the way we understand, monitor, and manage our health. Traditional healthcare has long been reactive—we wait until symptoms appear, then seek treatment. But what if we could predict and prevent health issues before they become serious problems?

Artificial intelligence, particularly in the realm of medical imaging, offers unprecedented capabilities to detect patterns and anomalies that escape even the most trained human eye. The retina, often called the window to the soul, is actually a window to our entire health system. Through advanced AI analysis of retinal images, we can now detect early signs of diabetes, hypertension, cardiovascular disease, and even neurological conditions.

This book will take you on a journey through this exciting frontier, showing you not just how the technology works, but how you can harness it for your own health and wellness. We'll explore real-world applications, examine case studies, and provide practical guidance for implementing AI-powered health monitoring in your daily life.

## The Science Behind Retinal Health Assessment

The human retina is a marvel of biological engineering, containing the only blood vessels in the body that can be directly observed without invasive procedures. This unique characteristic makes retinal imaging an invaluable tool for health assessment. When we examine the retina through advanced imaging techniques, we're essentially looking at a microcosm of the body's entire vascular system.

The retinal blood vessels reflect the health of blood vessels throughout the body. Changes in vessel diameter, branching patterns, and overall vascular architecture can indicate systemic health issues long before they manifest as noticeable symptoms. For instance, the earliest signs of diabetic retinopathy—microscopic changes in retinal blood vessels—can appear years before a patient experiences any vision problems.

Modern AI systems can analyze these subtle changes with remarkable precision. They can measure vessel widths down to the pixel level, detect minute hemorrhages, identify areas of poor blood flow, and even predict the likelihood of future cardiovascular events based on current retinal appearance.

*[This would continue for several more chapters with detailed technical content, case studies, and practical implementation guidance...]*

## Conclusion: Your Health, Your Future

As we reach the end of our exploration into AI-powered retinal health assessment, it's clear that we stand at the threshold of a new era in personalized healthcare. The technologies we've discussed throughout this book are not distant future possibilities—they're available today and rapidly becoming more accessible to individuals and healthcare providers alike.

The journey from reactive to proactive healthcare requires not just technological advancement, but a fundamental shift in how we think about health monitoring and disease prevention. By embracing AI-powered tools and incorporating them into our regular health routines, we can take unprecedented control over our health outcomes.

Remember that technology is a tool, not a replacement for professional medical care. The insights provided by AI systems should complement, not substitute for, regular medical checkups and professional healthcare guidance. The goal is to create a more informed, more engaged relationship between you, your healthcare providers, and your long-term health.

The future of healthcare is personalized, predictive, and participatory. By understanding and adopting these technologies today, you're not just improving your own health prospects—you're contributing to a global transformation in how humanity approaches wellness and disease prevention."""
    }


def get_mock_chapter_response(chapter_number: int = 1, section_name: str = "Mock Chapter") -> Dict[str, Any]:
    """Mock single chapter response."""
    mock_content = f"""# {section_name}

This is a comprehensive chapter covering the essential aspects of {section_name.lower()}. In this chapter, we'll explore the fundamental concepts, practical applications, and real-world implications of this important topic.

## Key Concepts

The foundation of understanding {section_name.lower()} begins with recognizing its critical role in the broader context of AI-powered healthcare. This chapter will guide you through:

- The theoretical underpinnings of the technology
- Practical implementation strategies
- Real-world case studies and examples
- Best practices for optimal results
- Common pitfalls and how to avoid them

## Detailed Analysis

Moving beyond the basics, we delve into the nuanced aspects that make this topic particularly relevant to modern healthcare applications. The integration of artificial intelligence with traditional medical practices requires careful consideration of both technical capabilities and clinical needs.

The evidence supporting these approaches comes from extensive research and clinical trials conducted across multiple healthcare systems. Studies have consistently shown significant improvements in early detection rates, diagnostic accuracy, and patient outcomes when these technologies are properly implemented.

## Practical Applications

In real-world scenarios, the application of these principles has led to remarkable breakthroughs in patient care. Healthcare providers report enhanced diagnostic capabilities, improved patient engagement, and more efficient use of medical resources.

The technology's ability to process and analyze vast amounts of data in real-time has revolutionized how medical professionals approach screening, diagnosis, and treatment planning. This transformation extends beyond individual patient care to population health management and public health initiatives.

## Future Implications

Looking ahead, the continued evolution of these technologies promises even greater advances in healthcare delivery. The convergence of AI, machine learning, and medical imaging will likely produce capabilities we can barely imagine today.

As these tools become more sophisticated and accessible, we can expect to see their integration into routine healthcare practices, ultimately leading to better health outcomes for individuals and communities worldwide.

## Conclusion

This chapter has provided a comprehensive overview of {section_name.lower()}, highlighting both current applications and future potential. The key takeaways emphasize the importance of understanding both the technical aspects and practical implications of implementing these advanced healthcare technologies.

The journey toward AI-enhanced healthcare is not just about adopting new tools—it's about fundamentally reimagining how we approach health, wellness, and medical care in the 21st century."""

    return {
        "chapter_number": chapter_number,
        "section_name": section_name,
        "content": mock_content,
        "word_count": len(mock_content.split()),
        "generation_time": 12.5,
        "cost_estimate": 0.15
    }


def get_mock_book_chapters_response(chapters_to_generate: List[int] = [1]) -> Dict[str, Any]:
    """Mock response for /generate-book-chapters endpoint."""
    toc = get_mock_toc_response()
    chapters = []
    
    for chapter_num in chapters_to_generate:
        if chapter_num <= len(toc):
            section = toc[chapter_num - 1]
            chapter = get_mock_chapter_response(
                chapter_number=chapter_num,
                section_name=section["section_name"]
            )
            chapters.append(chapter)
    
    return {
        "toc": toc,
        "chapters": chapters,
        "generated_chapters": chapters_to_generate,
        "total_estimated_cost": len(chapters) * 0.15 + 0.05,  # chapters + TOC cost
        "total_generation_time": len(chapters) * 12.5 + 3.2,  # chapters + TOC time
        "metadata": {
            "title": "Eyes on Health: AI-Powered Retinal Imaging for Wellness",
            "author": "Richard Sprague",
            "book_idea": "AI-powered retinal imaging for wellness assessment",
            "total_chapters_in_toc": len(toc),
            "chapters_requested": len(chapters_to_generate),
            "chapters_generated": len(chapters)
        }
    }


def get_mock_book_generation_response() -> Dict[str, Any]:
    """Mock response for full book generation."""
    toc = get_mock_toc_response()
    chapters = []
    
    for i, section in enumerate(toc):
        chapter = get_mock_chapter_response(
            chapter_number=i + 1,
            section_name=section["section_name"]
        )
        chapters.append(chapter)
    
    total_words = sum(chapter["word_count"] for chapter in chapters)
    total_time = sum(chapter["generation_time"] for chapter in chapters)
    total_cost = sum(chapter["cost_estimate"] for chapter in chapters)
    
    return {
        "chapters": chapters,
        "total_word_count": total_words,
        "total_generation_time": total_time,
        "total_cost_estimate": total_cost,
        "generation_summary": {
            "total_chapters": len(chapters),
            "average_chapter_length": total_words // len(chapters),
            "average_generation_time": total_time / len(chapters),
            "generation_method": "mock_sequential"
        }
    }


def get_mock_test_response() -> Dict[str, Any]:
    """Mock response for /test endpoint."""
    return {
        "message": "AI Book Generator API is up and running! [MOCK MODE]",
        "architecture": "modular_chapter_by_chapter",
        "mock_mode": True,
        "available_endpoints": [
            "/toc", 
            "/draft", 
            "/generate-chapter", 
            "/generate-book", 
            "/generate-book-chapters",
            "/pdf", 
            "/cover", 
            "/demo", 
            "/demo/presets"
        ],
        "mock_endpoints": [
            "/mock/toc",
            "/mock/draft", 
            "/mock/generate-chapter", 
            "/mock/generate-book", 
            "/mock/generate-book-chapters",
            "/mock/test"
        ],
        "debug_env": {
            "API_BASE_URL": "MOCK_MODE",
            "HAL9_TOKEN_present": "MOCK_MODE"
        }
    }


# Mapping function to get appropriate mock response
def get_mock_response(endpoint: str, request_data: Any = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Get mock response for specified endpoint.
    
    Args:
        endpoint: API endpoint name (e.g., 'toc', 'draft', 'chapter')
        request_data: Request data (used for context-specific responses)
    
    Returns:
        Dict containing mock response data
    """
    if endpoint == "toc":
        book_idea = getattr(request_data, 'book_idea', '') if request_data else ''
        return get_mock_toc_response(book_idea)
    
    elif endpoint == "draft":
        return get_mock_draft_response()
    
    elif endpoint == "generate-chapter":
        # Handle Pydantic model properly
        if request_data and hasattr(request_data, 'chapter_outline'):
            chapter_outline = request_data.chapter_outline
            chapter_num = getattr(chapter_outline, 'chapter_number', 1)
            section_name = getattr(chapter_outline, 'section_name', 'Mock Chapter')
        else:
            chapter_num = 1
            section_name = 'Mock Chapter'
        return get_mock_chapter_response(chapter_num, section_name)
    
    elif endpoint == "generate-book":
        return get_mock_book_generation_response()
    
    elif endpoint == "generate-book-chapters":
        chapters = getattr(request_data, 'chapters_to_generate', [1]) if request_data else [1]
        return get_mock_book_chapters_response(chapters)
    
    elif endpoint == "test":
        return get_mock_test_response()
    
    elif endpoint == "pdf":
        # For PDF, we'll return mock file path since we can't generate mock PDF bytes easily
        return {"mock_pdf": "mock_data/Eyes_on_Health_cover.pdf", "message": "Mock PDF generation - would return PDF bytes"}
    
    elif endpoint == "cover":
        # For cover, reference existing mock PDF
        return {"mock_cover": "mock_data/Eyes_on_Health_cover.pdf", "message": "Mock cover generation - would return cover PDF bytes"}
    
    else:
        return {"error": f"No mock response defined for endpoint: {endpoint}"}