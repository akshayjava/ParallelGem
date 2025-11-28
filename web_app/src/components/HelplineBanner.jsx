import React from 'react';

const HelplineBanner = () => {
    return (
        <div className="helpline-banner">
            <div className="helpline-content">
                <h3>⚠️ Help is Available</h3>
                <p>If you or someone you know is struggling or in immediate danger, please reach out for help.</p>
                <div className="helpline-numbers">
                    <div className="helpline-item">
                        <strong>🇺🇸 USA (988 Lifeline):</strong>
                        <a href="tel:988">988</a>
                    </div>
                    <div className="helpline-item">
                        <strong>🇬🇧 UK (Samaritans):</strong>
                        <a href="tel:116123">116 123</a>
                    </div>
                    <div className="helpline-item">
                        <strong>Emergency:</strong>
                        <a href="tel:911">911 (US)</a> / <a href="tel:999">999 (UK)</a>
                    </div>
                </div>
                <p className="disclaimer">
                    This is a research demo for AI safety. The content below contains synthetic examples of sensitive topics.
                    <strong> Viewer discretion is advised.</strong>
                </p>
            </div>
        </div>
    );
};

export default HelplineBanner;
