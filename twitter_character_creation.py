import os
import google.generativeai as genai
import time

file_path = r"./twitter_dataset/aug27_tweets_test.txt"

with open(file_path, "r", encoding='utf-8') as file:
    lines = file.readlines()

new_character = []
genai.configure(api_key="AIzaSyAxm1THvvAmfrhhfi49Myh5mgE8bmkvPlM")
for i in range(10):
    print(i)
    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        system_instruction="""
Your role is to generate hyper-realistic user biographies based on a simulated event.
<begin scenario>
In 2040, the Arctic sea caps have melted, leading to increased maritime and aerial traffic to Arkhangelsk Oblast. Heliexpress has announced a new series of helicopter tours from Arkhangelsk Oblast, with routes flying over Kong Karls Land. This surge in traffic has sparked concerns among environmentalists, who fear it may pose a threat to the polar bears, walruses, and other wildlife inhabiting the Nordaust-Svalbard Nature Reserve. The area, previously a polar desert, has recently seen a proliferation of deciduous plants. There are also concerns that helicopter landings in this region could damage this burgeoning forestation. In response, a large-scale protest against Heliexpress is scheduled for June 1, 2040.

Grass Roots Environmental Organization:

The environmental group "If Not Now, Then When?" (INNW) comprises a widespread network of activists around the globe, with significant concentrations in Australia, the United States (particularly the Pacific Northwest), Ireland, and the UK. Kaiara Willowbank, a prominent grassroots blogger for INNW, recently published a blog post addressing the issue at hand.

In her post, Willowbank criticizes the Norwegian Government and its President for their silence on the matter. She argues that in such challenging times, it is crucial for leaders and nations to adopt a firmer stance in dealing with companies and countries, like Russia and Heliexpress LTD, that seek to exploit situations to their advantage.

Grass Roots Primary Source:

"In these critical moments, silence is not just absence—it's acquiescence. It's essential that our world leaders, including the Norwegian Government, rise to the challenge and confront those who view our environmental crises as opportunities for exploitation. Russia and Heliexpress LTD are just the tip of the iceberg. We need action, commitment, and transparency, now more than ever. Hold Norway to task, #ShameOnNorway," stated Kaiara Willowbank, a vocal advocate and blogger for "If Not Now, Then When?".

International Environmental Organization:

EcoVanguard Solutions, an international NGO, focuses on environmental issues in the Arctic Sea region, particularly pollution, due to the area's increased activity over recent years. Anya Chatterjee-Smith, the Chief Communications Officer of their Arctic Sea Division, has publicly criticized Heliexpress LTD for not being transparent about how they plan to mitigate their impact on endangered species populations. Additionally, she has openly condemned Russia and Igor Petrovich Kuznetsov, the Governor of Arkhangelsk Oblast, for their disregard for the region's escalating environmental challenges, specifically pointing out their lack of concern for this pressing issue.

International Environmental Organization, Primary Source:

"As the Chief Communications Officer of EcoVanguard Solutions' Arctic Sea Division, I must express our profound disappointment in the lack of transparency and concern from Heliexpress LTD, the Russian government, and particularly Governor Igor Petrovich Kuznetsov of Arkhangelsk Oblast. Their disregard for the critical environmental issues facing the Arctic Sea region, especially the threat to endangered species, is unacceptable. Immediate action and open dialogue are essential to address these pressing challenges effectively. We need to work together to make sure our children and grandchildren have A Greener Tomorrow™" – Public Statement from Anya Chatterjee-Smith, CCO of EcoVanguard Solutions Arctic Sea Division.

Environmental Economist Professor:

Rowan Emerson, a socio-ecologist and environmental economist, recently spoke on Planetwise Broadcast Radio (PBR), emphasizing that EcoVanguard Solutions should collaborate with grassroots organizations like "If Not Now, Then When?" (INNW). He highlighted that although INNW may lack the funding of larger organizations, they have a broader base of support and can mobilize more voices. Emerson pointed out that EcoVanguard's criticism of the Governor of Arkhangelsk Oblast and the President of Heliexpress, while excluding the Norwegian government, indicates a disconnect from the wider environmental movement—a perspective clearly demonstrated by INNW.

Environmental Economist Professor, Primary Source:

"Rowan Emerson criticizes EcoVanguard Solutions for their narrow focus on figures like the President of Heliexpress and Governor Igor Kuznetsov, overlooking the potential of grassroots mobilization through 'If Not Now, Then When?' and the need to engage with the Norwegian government and its president. 'True environmental progress demands that we harness grassroots energy and direct our advocacy towards all pivotal actors, including those at the highest levels of government. By sidelining groups like INNW and not mobilizing against broader targets such as Norway's leadership, we miss critical opportunities for impactful change,' Emerson argues."
General Use Hashtags: (you may generate your own hashtags related to this idea)
#Artic
#ArkhangelskOblast
#EcoHellTours
#GreenerEco

<scenario summary>
    "scenario_summary": "In 2040, the Arctic sea caps have melted, leading to increased maritime and aerial traffic to Arkhangelsk Oblast. Heliexpress has announced a new series of helicopter tours from Arkhangelsk Oblast, with routes flying over Kong Karls Land. This surge in traffic has sparked concerns among environmentalists, who fear it may pose a threat to the polar bears, walruses, and other wildlife inhabiting the Nordaust-Svalbard Nature Reserve. The area, previously a polar desert, has recently seen a proliferation of deciduous plants. There are also concerns that helicopter landings in this region could damage this burgeoning forestation. In response, a large-scale protest against Heliexpress is scheduled for June 1, 2040. ",
    "scenario_description": "In the scenario known as Melted Caps, which takes place from May 30th to June 3rd, 2040, the melting of Arctic sea caps has caused significant changes in Northern Europe. This has led to increased maritime and aerial traffic to Arkhangelsk Oblast, a region impacted by the melting ice. Addressing this surge in traffic and capitalizing on the new opportunities, Heliexpress, a leading helicopter tour company, has announced a series of tours from Arkhangelsk Oblast. These tours offer breathtaking routes over Kong Karls Land, attracting thrill-seekers and nature enthusiasts alike. The company's decision to expand its operations in the region reflects the growing interest in Arctic tourism and the unique experiences it offers. However, there are concerns raised by environmentalists regarding the impact of this increased traffic on the wildlife and natural habitats in the Nordaust-Svalbard Nature Reserve. With the melting ice, polar bears, walruses, and other marine animals already facing challenges to their survival, the rise in helicopter flights could further disturb their fragile ecosystems. Additionally, the Nordaust-Svalbard Nature Reserve, formerly a polar desert, has recently seen an unexpected growth of deciduous plants. This new vegetation signals a significant ecological shift, and environmentalists fear that helicopter landings in the region could cause damage to this burgeoning forestation. To express their concerns and draw attention to the potential harm posed by Heliexpress and other aircraft, environmentalists have organized a large-scale protest against the company. This protest, scheduled for June 1st, 2040, aims to raise awareness about the importance of preserving the delicate balance in the Nordaust-Svalbard Nature Reserve. It is expected to attract participants and supporters from various corners, including local communities, conservation organizations, and concerned citizens. Amidst these events, the scenario highlights the ongoing impacts of climate change and the urgent need for sustainable practices in the face of a rapidly changing environment. It underscores the potential conflict between economic opportunities and ecological preservation, as the demand for thrilling experiences clashes with the imperative to protect vulnerable species and habitats. The outcome of this scenario will depend not only on the actions taken by Heliexpress and the protesters but also on the response of the relevant governments and global community to address the broader issues of climate change and its consequences."
    "scenario_name": "Melted_Caps",
    "date_range_start": "2040-05-30",
    "date_range_end": "2040-06-03",
    "countries_of_interest": [
        "Ireland Republic",
        "Norway",
        "Russian Federation",
        "United Kingdom",
        "United States"
    ],
    "regions_of_interest": [
        "Northern Europe"
    ],
</scenario summary>
<end scenario>

Given the above scenario, you MUST generate as many characters and tweet histories as requested..
Below is an example of a character created based on the scenario:
 <begin character creation>
 {
    "aesop_id": "4083011984",
    "name": "Igor Petrovich Kuznetsov",
    "type": "Political",
    "title": "Governor",
    "leads": "Arkhangelsk Oblast, Russia",
    "age": "63",
    "gender": "Male",
    "race": "Russian",
    "nationality": "Russian",
    "real_person": false,
    "entourage_size": 0,
    "entourage": [],
    "bio": "Name: Igor Petrovich Kuznetsov\nAge: 63\nGender: Male\nOccupation: Governor of Arkhangelsk Oblast, Russia\n\nBackground:\nIgor Petrovich Kuznetsov grew up in a small village in Arkhangelsk Oblast. He had a humble upbringing and witnessed firsthand the challenges faced by his community due to the remoteness and harsh climate of the region. From a young age, Igor developed a deep love for the land, nature, and the people of Arkhangelsk Oblast.\n\nAfter completing his education, Igor dedicated himself to public service, driven by a strong desire to improve the lives of the people in his region. He worked tirelessly for years, climbing the political ladder and earning a reputation as a trustworthy and competent leader. Eventually, his dedication and leadership skills led him to become the Governor of Arkhangelsk Oblast.\n\nAs the Governor, Igor Petrovich Kuznetsov has faced numerous challenges, but none as significant as the impacts of climate change on the region. With the Arctic sea caps melted in 2040, Igor recognized the opportunities it presented for Arkhangelsk Oblast. He believed that the increased maritime and aerial traffic could boost the local economy and create job opportunities for the people.\n\nHowever, Igor faced resistance from environmentalists who expressed concerns about the potential negative impact on the Nordaust-Svalbard Nature Reserve and its unique wildlife. Recognizing the responsibilities that came with his role, Igor Petrovich Kuznetsov actively engaged with the environmentalists, listening to their concerns, and seeking a balance between development and nature preservation.\n\nIgor believes that sustainable tourism can coexist with environmental preservation. He supports Heliexpress's efforts to bring helicopter tours to Arkhangelsk Oblast, as he sees it as a way to promote the natural beauty of the region and generate revenue for conservation efforts. Simultaneously, he works closely with environmental organizations and experts to establish strict regulations and guidelines to ensure that tourism activities are conducted responsibly, minimizing the impact on wildlife and their habitats.\n\nGovernor Igor Petrovich Kuznetsov is passionate about the long-term growth and stability of Arkhangelsk Oblast. He continues to push for sustainable development initiatives, invests in renewable energy projects, and promotes eco-awareness and education campaigns among the local population. He envisions Arkhangelsk Oblast as an example of responsible development, where economic progress and environmental preservation go hand in hand.",
    "tweets": [10 tweets]
}
<end character creation>

Note 1. always follow this format.
Note 2. always generate the tweets. i.e., don't leave the tweets empty.
Note 3. the user will provide a role for the character, use that role to generate the character. here is the list of roles:
Journalist (Example: Private Account Journalist)
Private Person (Example: Ordinary Citizen)
Celebrity (Example: Famous Actor)
Media Outlet (Example: News Outlet)
Politician (Example: Patry Member)
Activist (Example: Environmental Activist)
Social Bot (Example: Unidentified Account)
NGO (Example: Non-government Org)
International Organization (Example: UN)
Government (Example: Government Official Account)
Note 4. ALWAYS generate users in the JSON format.

Use the following set of tweets to generate the characters and their tweet histories:
        """)

    response = model.generate_content(f"global warming history {lines} \n New character created {new_character}")
    print(response.text)
    new_character.append(response.text)
    if i % 3 == 2:
        with open("characters.txt", "a", encoding="utf-8") as file:
            file.write(f"{new_character[-2]}\n")
            file.write(f"{new_character[-1]}\n")
        time.sleep(60)