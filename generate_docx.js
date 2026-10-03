const fs = require('fs');
const path = require('path');
const docx = require('C:/Users/USERAS/.gemini/antigravity-ide/brain/87631bbd-3e5f-4d7b-b034-9ead2bc6da1b/scratch/node_modules/docx');

const {
    Document,
    Paragraph,
    TextRun,
    Table,
    TableRow,
    TableCell,
    ImageRun,
    Packer,
    PageNumber,
    AlignmentType,
    WidthType,
    BorderStyle,
    ShadingType,
    Footer
} = docx;

// Output paths
const outputPath = path.resolve(__dirname, 'report/CSE307_Term_Paper_202414064.docx');
const imagePath = path.resolve(__dirname, 'results/before_after_shift.png');

// Colors
const COLOR_PRIMARY = '0F2D59';    // Dark Navy
const COLOR_SECONDARY = '1E3A8A';  // Muted Navy
const COLOR_BODY = '1A1A1A';       // Soft Black
const COLOR_MUTED = '4B5563';      // Muted Gray
const COLOR_BORDER = 'D0D7DE';     // Light Border Gray
const COLOR_TH_BG = 'F0F4F8';      // Table Header Background
const COLOR_ZEBRA = 'F9FBFC';      // Alternate Row Background

// Typography settings (Times New Roman)
const FONT_FAMILY = 'Times New Roman';
const BODY_SIZE = 22;      // 11 pt
const H1_SIZE = 25;        // 12.5 pt
const H2_SIZE = 23;        // 11.5 pt
const META_SIZE = 20;      // 10 pt
const TABLE_SIZE = 18;     // 9 pt
const CAPTION_SIZE = 19;   // 9.5 pt
const LINE_SPACING = 255;  // ~1.10 line spacing

// Helper functions for building elements
function createHeading1(text, options = {}) {
    return new Paragraph({
        pageBreakBefore: options.pageBreakBefore || false,
        keepWithNext: true,
        spacing: { before: options.before !== undefined ? options.before : 120, after: 35, line: LINE_SPACING },
        children: [
            new TextRun({
                text: text,
                bold: true,
                size: H1_SIZE,
                font: FONT_FAMILY,
                color: COLOR_PRIMARY
            })
        ]
    });
}

function createHeading2(text, options = {}) {
    return new Paragraph({
        pageBreakBefore: options.pageBreakBefore || false,
        keepWithNext: true,
        spacing: { before: options.before !== undefined ? options.before : 90, after: 25, line: LINE_SPACING },
        children: [
            new TextRun({
                text: text,
                bold: true,
                size: H2_SIZE,
                font: FONT_FAMILY,
                color: COLOR_SECONDARY
            })
        ]
    });
}

function createBodyParagraph(textRuns, options = {}) {
    const children = typeof textRuns === 'string'
        ? [new TextRun({ text: textRuns, size: BODY_SIZE, font: FONT_FAMILY, color: COLOR_BODY })]
        : textRuns;

    return new Paragraph({
        alignment: options.alignment || AlignmentType.JUSTIFIED,
        spacing: {
            before: options.before || 0,
            after: options.after !== undefined ? options.after : 45,
            line: LINE_SPACING
        },
        children: children
    });
}

function createBulletItem(leadBold, restText) {
    return new Paragraph({
        bullet: { level: 0 },
        alignment: AlignmentType.JUSTIFIED,
        spacing: { before: 8, after: 25, line: LINE_SPACING },
        children: [
            new TextRun({
                text: leadBold + ' ',
                bold: true,
                size: BODY_SIZE,
                font: FONT_FAMILY,
                color: COLOR_BODY
            }),
            new TextRun({
                text: restText,
                size: BODY_SIZE,
                font: FONT_FAMILY,
                color: COLOR_BODY
            })
        ]
    });
}

function createNumberedItem(numberStr, leadBold, restText) {
    return new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { before: 8, after: 25, line: LINE_SPACING },
        indent: { left: 320, hanging: 320 },
        children: [
            new TextRun({
                text: numberStr + '\t',
                bold: true,
                size: BODY_SIZE,
                font: FONT_FAMILY,
                color: COLOR_PRIMARY
            }),
            leadBold ? new TextRun({
                text: leadBold + ' ',
                bold: true,
                size: BODY_SIZE,
                font: FONT_FAMILY,
                color: COLOR_BODY
            }) : new TextRun({ text: '' }),
            new TextRun({
                text: restText,
                size: BODY_SIZE,
                font: FONT_FAMILY,
                color: COLOR_BODY
            })
        ]
    });
}

function createReferenceItem(refNum, authorTitle, restDetails) {
    return new Paragraph({
        alignment: AlignmentType.LEFT,
        spacing: { before: 6, after: 25, line: LINE_SPACING },
        indent: { left: 320, hanging: 320 },
        children: [
            new TextRun({
                text: refNum + '\t',
                bold: true,
                size: BODY_SIZE,
                font: FONT_FAMILY,
                color: COLOR_PRIMARY
            }),
            new TextRun({
                text: authorTitle + ' ',
                size: BODY_SIZE,
                font: FONT_FAMILY,
                color: COLOR_BODY
            }),
            new TextRun({
                text: restDetails,
                size: BODY_SIZE,
                font: FONT_FAMILY,
                color: COLOR_BODY
            })
        ]
    });
}

// Table cell borders
const standardBorder = {
    top: { style: BorderStyle.SINGLE, size: 4, color: COLOR_BORDER },
    bottom: { style: BorderStyle.SINGLE, size: 4, color: COLOR_BORDER },
    left: { style: BorderStyle.SINGLE, size: 4, color: COLOR_BORDER },
    right: { style: BorderStyle.SINGLE, size: 4, color: COLOR_BORDER }
};

// Build Table 1
function buildResultsTable() {
    const colWidths = [1346, 1720, 1720, 1720, 1620, 1620];

    const headers = [
        'Algorithm',
        'Phase 1 Hits / Faults (Hit %)',
        'Phase 2 Hits / Faults (Hit %)',
        'Overall Hits / Faults (Hit %)',
        'Hit Ratio Drop (Pct. Points)',
        'Relative Drop (%)'
    ];

    const headerRow = new TableRow({
        tableHeader: true,
        cantSplit: true,
        children: headers.map((h, i) => new TableCell({
            width: { size: colWidths[i], type: WidthType.DXA },
            shading: { type: ShadingType.CLEAR, fill: COLOR_TH_BG },
            borders: standardBorder,
            margins: { top: 80, bottom: 80, left: 80, right: 80 },
            children: [
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({
                            text: h,
                            bold: true,
                            size: TABLE_SIZE,
                            font: FONT_FAMILY,
                            color: COLOR_PRIMARY
                        })
                    ]
                })
            ]
        }))
    });

    const rowsData = [
        ['FIFO', '318 / 182 (63.60%)', '100 / 400 (20.00%)', '418 / 582 (41.80%)', '43.60%', '68.55%'],
        ['LRU', '337 / 163 (67.40%)', '100 / 400 (20.00%)', '437 / 563 (43.70%)', '47.40%', '70.33%'],
        ['Optimal', '408 / 92 (81.60%)', '218 / 282 (43.60%)', '626 / 374 (62.60%)', '38.00%', '46.57%'],
        ['Learned', '330 / 170 (66.00%)', '100 / 400 (20.00%)', '430 / 570 (43.00%)', '46.00%', '69.70%']
    ];

    const dataRows = rowsData.map((row, rIdx) => {
        const isZebra = rIdx % 2 === 1;
        return new TableRow({
            cantSplit: true,
            children: row.map((cellText, cIdx) => new TableCell({
                width: { size: colWidths[cIdx], type: WidthType.DXA },
                shading: isZebra ? { type: ShadingType.CLEAR, fill: COLOR_ZEBRA } : undefined,
                borders: standardBorder,
                margins: { top: 65, bottom: 65, left: 80, right: 80 },
                children: [
                    new Paragraph({
                        alignment: cIdx === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
                        children: [
                            new TextRun({
                                text: cellText,
                                bold: cIdx === 0,
                                size: TABLE_SIZE,
                                font: FONT_FAMILY,
                                color: COLOR_BODY
                            })
                        ]
                    })
                ]
            }))
        });
    });

    return new Table({
        width: { size: 9746, type: WidthType.DXA },
        alignment: AlignmentType.CENTER,
        rows: [headerRow, ...dataRows]
    });
}

function generateDocx() {
    const imgData = fs.readFileSync(imagePath);

    const doc = new Document({
        styles: {
            default: {
                document: {
                    run: {
                        font: FONT_FAMILY,
                        size: BODY_SIZE,
                        color: COLOR_BODY
                    }
                }
            }
        },
        sections: [{
            properties: {
                page: {
                    size: {
                        width: 11906,  // A4: 210mm
                        height: 16838  // A4: 297mm
                    },
                    margin: {
                        top: 960,      // ~0.67 inch
                        bottom: 960,   // ~0.67 inch
                        right: 1080,   // 0.75 inch
                        left: 1080     // 0.75 inch
                    }
                }
            },
            footers: {
                default: new Footer({
                    children: [
                        new Paragraph({
                            alignment: AlignmentType.CENTER,
                            children: [
                                new TextRun({
                                    text: 'Page ',
                                    font: FONT_FAMILY,
                                    size: META_SIZE,
                                    color: COLOR_MUTED
                                }),
                                new TextRun({
                                    children: [PageNumber.CURRENT],
                                    font: FONT_FAMILY,
                                    size: META_SIZE,
                                    color: COLOR_MUTED
                                }),
                                new TextRun({
                                    text: ' of ',
                                    font: FONT_FAMILY,
                                    size: META_SIZE,
                                    color: COLOR_MUTED
                                }),
                                new TextRun({
                                    children: [PageNumber.TOTAL_PAGES],
                                    font: FONT_FAMILY,
                                    size: META_SIZE,
                                    color: COLOR_MUTED
                                })
                            ]
                        })
                    ]
                })
            },
            children: [
                // Title
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    spacing: { before: 0, after: 70 },
                    children: [
                        new TextRun({
                            text: 'Learning-Augmented Page Replacement: Classical Algorithms Under Workload Shift',
                            bold: true,
                            size: 30, // 15 pt
                            font: FONT_FAMILY,
                            color: COLOR_PRIMARY
                        })
                    ]
                }),

                // Metadata block
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    spacing: { before: 0, after: 20 },
                    children: [
                        new TextRun({ text: 'Course: ', bold: true, size: META_SIZE, font: FONT_FAMILY }),
                        new TextRun({ text: 'CSE-307 Operating Systems    |    ', size: META_SIZE, font: FONT_FAMILY }),
                        new TextRun({ text: 'Section: ', bold: true, size: META_SIZE, font: FONT_FAMILY }),
                        new TextRun({ text: 'B', size: META_SIZE, font: FONT_FAMILY })
                    ]
                }),
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    spacing: { before: 0, after: 20 },
                    children: [
                        new TextRun({ text: 'Student Name: ', bold: true, size: META_SIZE, font: FONT_FAMILY }),
                        new TextRun({ text: 'Mahin Ar Rahman    |    ', size: META_SIZE, font: FONT_FAMILY }),
                        new TextRun({ text: 'Student ID: ', bold: true, size: META_SIZE, font: FONT_FAMILY }),
                        new TextRun({ text: '202414064', size: META_SIZE, font: FONT_FAMILY })
                    ]
                }),
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    spacing: { before: 0, after: 70 },
                    children: [
                        new TextRun({ text: 'GitHub Repository: ', bold: true, size: META_SIZE, font: FONT_FAMILY }),
                        new TextRun({ text: 'https://github.com/Mahin13377/OS-Term-Paper', size: META_SIZE, font: FONT_FAMILY, color: COLOR_PRIMARY })
                    ]
                }),

                // Horizontal dividing rule
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    spacing: { before: 0, after: 70 },
                    border: {
                        bottom: { style: BorderStyle.SINGLE, size: 6, color: COLOR_BORDER }
                    },
                    children: []
                }),

                // 1. Problem Framing
                createHeading1('1. Problem Framing', { before: 0 }),
                createBodyParagraph(
                    "In virtual memory systems, the operating system manages memory using fixed-size pages. When a referenced virtual page is not currently mapped to a valid physical frame, the processor raises a page-fault exception and the operating system's page-fault handler responds. The operating system must load the missing page from secondary storage into an available frame. If all frames are occupied, a page-replacement algorithm must select a resident victim page to evict."
                ),
                createBodyParagraph(
                    "Because secondary storage is orders of magnitude slower than main memory, page faults incur severe execution penalties. Classical policies rely on static heuristics: FIFO evicts the oldest resident page, while LRU evicts the page unreferenced for the longest duration."
                ),
                createBodyParagraph(
                    "However, real programs exhibit non-stationary workloads where access patterns shift over time, such as transitioning from tight loops to scanning large datasets or performing random lookups. Under such shifts, classical heuristics can degrade sharply. This paper evaluates FIFO, LRU, Optimal, and a lightweight learning-augmented Decision Tree policy, examining how an abrupt shift from localized to random access affects their performance."
                ),

                // 2. Classical Page-Replacement Algorithms
                createHeading1('2. Classical Page-Replacement Algorithms'),
                createHeading2('2.1 First-In, First-Out (FIFO)'),
                createBodyParagraph(
                    "FIFO tracks resident pages in an arrival queue. On a replacement fault, the page that entered memory earliest is evicted. Although FIFO has minimal bookkeeping overhead, it frequently evicts heavily used pages and can exhibit Belady's Anomaly."
                ),
                createHeading2('2.2 Least Recently Used (LRU)'),
                createBodyParagraph(
                    "LRU records the logical access time of each page, evicting the page with the oldest access timestamp. LRU performs well on workloads with strong temporal locality. However, tracking access history adds runtime overhead, and performance declines when working sets exceed frame capacity."
                ),
                createHeading2("2.3 Optimal / Belady's Min Algorithm"),
                createBodyParagraph(
                    "Belady's Optimal algorithm establishes the theoretical performance limit for page replacement. When an eviction occurs, Optimal inspects future references and evicts the resident page whose next use is farthest in the future. Because an operating system cannot predict future accesses, Optimal is unimplementable online. Nonetheless, it defines the lowest achievable fault count and serves as an oracle to generate supervision labels for machine learning."
                ),

                // 3. Learned / Adaptive Component
                createHeading1('3. Learned / Adaptive Component'),
                createBodyParagraph(
                    "Rather than deploying complex neural networks that introduce prohibitive latency into operating system kernels, this project uses an explainable, lightweight policy based on scikit-learn's DecisionTreeClassifier."
                ),
                createHeading2('3.1 Feature Representation'),
                createBodyParagraph(
                    "Whenever a page fault requires an eviction, each candidate page p resident in memory is characterized by three lightweight features:"
                ),
                createBulletItem('Recency:', 'Memory accesses elapsed since page p was last referenced (current index - last-used index).'),
                createBulletItem('Frequency:', 'References to page p within a sliding window of the last W = 50 accesses.'),
                createBulletItem('Age:', 'Elapsed accesses since page p entered its frame (current index - arrival index).'),

                // 3.2 Oracle Supervision and Training (Starts cleanly at Page 2)
                createHeading2('3.2 Oracle Supervision and Training', { pageBreakBefore: true, before: 0 }),
                createBodyParagraph(
                    "Training data is extracted from independent synthetic traces to prevent data leakage. During training, the Optimal algorithm is simulated on these traces. At each eviction point, every candidate page yields one sample with its feature vector. The binary label is y = 1 if Optimal evicted that candidate, and y = 0 otherwise."
                ),
                createBodyParagraph(
                    "A shallow decision tree (max_depth = 5, min_samples_split = 10) is trained on these records. The resulting model is compact (29 leaf nodes) and explainable, attributing 61.5% importance to age, 30.0% to recency, and 8.5% to frequency."
                ),
                createHeading2('3.3 Online Decision-Making and Fallback'),
                createBodyParagraph(
                    "During execution, when the learned policy encounters a page fault with full frames, it computes candidate features, predicts eviction scores via the Decision Tree, and evicts the candidate with the highest predicted score. If candidate scores are tied, the policy defaults safely to LRU (evicting the candidate with maximum recency)."
                ),

                // 4. Experimental Setup
                createHeading1('4. Experimental Setup'),
                createBodyParagraph(
                    "The four policies were evaluated on an identical 1,000-reference synthetic test trace with a fixed random seed (seed=42):"
                ),
                createBulletItem('Phase 1: High Locality (Refs 0–499):', 'Small working set [0..5] with sequential loops and repeated accesses.'),
                createBulletItem('Workload Shift (Ref 500):', 'Access pattern shifts abruptly.'),
                createBulletItem('Phase 2: Low Locality (Refs 500–999):', 'Uniform random access across pages 0–19, eliminating locality.'),
                createBodyParagraph(
                    "Experiments evaluated frame sizes 3, 4, and 5, using 4 frames as the primary baseline. The Decision Tree was trained using four-frame training traces. The same trained model was then reused without retraining for the 3-, 4-, and 5-frame evaluations to observe how the learned policy transferred across different frame capacities."
                ),

                // 5. Results
                createHeading1('5. Results'),
                createBodyParagraph(
                    "Table 1 displays the empirical results obtained from executing the benchmark with 4 frames."
                ),
                new Paragraph({
                    keepWithNext: true,
                    spacing: { before: 60, after: 30 },
                    children: [
                        new TextRun({
                            text: 'Table 1: Performance Comparison Before and After Workload Shift (4 Frames)',
                            bold: true,
                            size: CAPTION_SIZE,
                            font: FONT_FAMILY,
                            color: COLOR_PRIMARY
                        })
                    ]
                }),
                buildResultsTable(),
                createBodyParagraph(
                    "Across other frame capacities:",
                    { before: 60, after: 20 }
                ),
                createBulletItem('3 Frames:', 'Overall hit ratios were 29.50% for FIFO (705 faults), 30.70% for LRU (693 faults), 33.80% for Learned (662 faults), and 50.90% for Optimal (491 faults).'),
                createBulletItem('5 Frames:', 'Overall hit ratios were 50.00% for FIFO (500 faults), 54.50% for LRU (455 faults), 54.00% for Learned (460 faults), and 71.00% for Optimal (290 faults).'),

                // Chart
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    keepWithNext: true,
                    spacing: { before: 50, after: 15 },
                    children: [
                        new ImageRun({
                            data: imgData,
                            transformation: {
                                width: 370,
                                height: 231
                            },
                            type: 'png'
                        })
                    ]
                }),
                new Paragraph({
                    alignment: AlignmentType.CENTER,
                    spacing: { before: 5, after: 50 },
                    children: [
                        new TextRun({
                            text: 'Figure 1: Hit Ratio Comparison Before and After Workload Shift (4 Frames)',
                            italics: true,
                            size: CAPTION_SIZE,
                            font: FONT_FAMILY,
                            color: COLOR_MUTED
                        })
                    ]
                }),

                // 6. Analysis of Workload Shift (Starts cleanly at Page 3)
                createHeading1('6. Analysis of Workload Shift', { pageBreakBefore: true, before: 0 }),
                createHeading2('6.1 Phase 1 (High Locality)', { before: 60 }),
                createBodyParagraph(
                    "In Phase 1, access was restricted to 6 pages across 4 frames:"
                ),
                createBulletItem('Optimal:', 'Attained an 81.60% hit ratio (92 faults).'),
                createBulletItem('LRU:', 'Achieved 67.40% (163 faults), surpassing FIFO at 63.60% (182 faults).'),
                createBulletItem('Learned:', 'Achieved 66.00% (170 faults), closely matching LRU.'),
                createBulletItem('Frame Sensitivity:', 'With 3 frames, the learned policy produced fewer faults than LRU (662 vs. 693 faults). One possible reason is that the model considered age and frequency in addition to recency, helping it avoid evicting pages that experienced brief pauses between iterations.'),

                createHeading2('6.2 Phase 2 (Uniform Random Access)', { before: 70 }),
                createBodyParagraph(
                    "At reference 500, the workload transitioned to uniform random access across pages 0–19:"
                ),
                createBulletItem('Hit Probability Baseline:', 'With four resident frames and 20 pages selected independently and uniformly, the expected hit probability for a history-based online policy is 4/20 = 20%. In this particular test trace, FIFO, LRU, and Learned each recorded exactly 20.00% during Phase 2.'),
                createBulletItem('Predictive Breakdown:', 'Because past references contain no information about future uniform random lookups, recency and frequency offer no predictive value.'),
                createBulletItem('Sharp Degradation:', 'Consequently, LRU dropped by 47.40 percentage points (70.33% relative decline), FIFO fell by 43.60 points (68.55%), and Learned fell by 46.00 points (69.70%).'),
                createBulletItem('Optimal Prescience:', 'Optimal achieved 43.60% because it evicts the resident page whose next use is farthest in the future, retaining pages that appear soonest.'),

                // 7. Limitations
                createHeading1('7. Limitations', { before: 80 }),
                createNumberedItem('1.', 'Kernel Overhead:', 'Software decision tree inference introduces latency unsuitable for microsecond-level page fault handling.'),
                createNumberedItem('2.', 'Feature Scope:', 'The model omits dirty-bit status (disk writeback costs) and multi-process contention.'),
                createNumberedItem('3.', 'Distribution Shift:', 'When access patterns diverge from training data, the model defaults to LRU fallback.'),

                // 8. Conclusion
                createHeading1('8. Conclusion', { before: 80 }),
                createBodyParagraph(
                    "This study evaluated FIFO, LRU, Optimal, and a learned replacement policy under an abrupt workload shift:"
                ),
                createNumberedItem('1.', '', 'Optimal provides an upper bound on achievable hit ratio and a lower bound on page faults (62.60% overall hit ratio vs. 41.80%–43.70% for online policies at 4 frames).'),
                createNumberedItem('2.', '', 'A compact 3-feature Decision Tree trained on oracle labels closely tracked LRU under high locality and produced fewer faults with 3 frames.'),
                createNumberedItem('3.', '', 'Under uniform random access, all online heuristics collapsed to the probabilistic baseline (20.00%). Learning-augmented policies are viable when access patterns exhibit structure, but cannot overcome an absence of temporal predictability.'),

                // 9. References
                createHeading1('9. References', { before: 80 }),
                createReferenceItem('1.', 'Abraham Silberschatz, Peter B. Galvin, and Greg Gagne.', 'Operating System Concepts. 10th Edition, John Wiley & Sons, 2018.'),
                createReferenceItem('2.', 'Andrew S. Tanenbaum and Herbert Bos.', 'Modern Operating Systems. 4th Edition, Pearson, 2014.'),
                createReferenceItem('3.', 'L. A. Belady.', '"A Study of Replacement Algorithms for a Virtual-Storage Computer." IBM Systems Journal, 5(2):78–101, 1966.'),
                createReferenceItem('4.', 'F. Pedregosa et al.', '"Scikit-learn: Machine Learning in Python." Journal of Machine Learning Research, 12:2825–2830, 2011.'),
                createReferenceItem('5.', 'Scikit-learn Documentation.', 'sklearn.tree.DecisionTreeClassifier. https://scikit-learn.org/stable/modules/tree.html')
            ]
        }]
    });

    Packer.toBuffer(doc).then(buffer => {
        fs.writeFileSync(outputPath, buffer);
        console.log(`[SUCCESS] Generated DOCX at: ${outputPath} (${buffer.length} bytes)`);
    }).catch(err => {
        console.error('[ERROR] Failed to generate DOCX:', err);
        process.exit(1);
    });
}

generateDocx();
