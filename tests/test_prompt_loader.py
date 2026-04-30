from app.services.prompt_loader import load_prompt_template, render_prompt


def test_load_prompt_template_reads_market_prompt():
    template = load_prompt_template("market")
    assert "startup market analysis agent" in template


def test_render_prompt_substitutes_context():
    rendered = render_prompt(
        "clarify",
        idea="Test idea",
        target_user="Founders",
        problem="Planning",
        monetization="Subscription",
        resources="Engineering",
        stage="idea",
        geography="US",
        notes="none",
    )
    assert "Test idea" in rendered
    assert "Founders" in rendered
